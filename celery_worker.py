import os
import logging
import asyncio
import uuid
from tempfile import NamedTemporaryFile
from typing import List, Optional

import httpx
from celery import Celery
from tenacity import retry, stop_after_attempt, wait_fixed
from moviepy.editor import (
    ImageClip,
    ColorClip,
    TextClip,
    CompositeVideoClip,
    concatenate_videoclips,
    concatenate_audioclips,
    AudioFileClip,
    VideoFileClip,  # for 3D model intro clips
    vfx,
)
from gtts import gTTS
import boto3
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adimage import AdImage
from facebook_business.adobjects.advideo import AdVideo
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.adcreative import AdCreative
from facebook_business.adobjects.ad import Ad

from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")

if not all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, S3_BUCKET_NAME]):
    raise ValueError("AWS credentials or S3 bucket not configured for Celery worker")


celery_app = Celery("tasks", broker=BROKER_URL, backend=BROKER_URL)

s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION,
)

retry_config = dict(stop=stop_after_attempt(3), wait=wait_fixed(2))

# Mapping of video template IDs to settings like target duration and
# optional placeholder video URLs used for the demo anime templates.
VIDEO_TEMPLATE_CONFIGS = {
    "standard": {
        "video_duration": 30,
        "model_intro_duration": 3,
        "outro_duration": 2,
        "final_outro_text": "Learn More at Our Website!",
        "text_fontsize": 48,
    },
    "fast_paced": {
        "video_duration": 15,
        "model_intro_duration": 2,
        "outro_duration": 2,
        "final_outro_text": "Check it out now!",
        "text_fontsize": 40,
    },
    "luxury_showcase": {
        "video_duration": 30,
        "model_intro_duration": 5,
        "outro_duration": 2,
        "final_outro_text": "Experience Luxury Today",
        "text_fontsize": 60,
    },
    "explainer": {
        "video_duration": 60,
        "model_intro_duration": 2,
        "outro_duration": 2,
        "final_outro_text": "Find out more on our site",
        "text_fontsize": 45,
    },
    "anime_10s": {
        "video_duration": 10,
        "placeholder_url": "https://example.com/anime_10s.mp4",
        "model_intro_duration": 0,
        "outro_duration": 2,
        "text_fontsize": 55,
        "final_outro_text": "ClipOpera Anime Ads!",
    },
    "anime_30s": {
        "video_duration": 30,
        "placeholder_url": "https://example.com/anime_30s.mp4",
        "model_intro_duration": 0,
        "outro_duration": 2,
        "text_fontsize": 50,
        "final_outro_text": "ClipOpera Anime Ads!",
    },
    "anime_60s": {
        "video_duration": 60,
        "placeholder_url": "https://example.com/anime_60s.mp4",
        "model_intro_duration": 0,
        "outro_duration": 2,
        "text_fontsize": 45,
        "final_outro_text": "ClipOpera Anime Ads!",
    },
    "ascii_art_ad": {
        "video_duration": 30,
        "placeholder_url": "https://example.com/ascii_art_ad.mp4",
        "model_intro_duration": 0,
        "outro_duration": 2,
        "text_fontsize": 40,
        "final_outro_text": "ASCII Ad by ClipOpera!",
    },
    "retro_8bit_ad": {
        "video_duration": 30,
        "placeholder_url": "https://example.com/retro_8bit_ad.mp4",
        "model_intro_duration": 0,
        "outro_duration": 2,
        "text_fontsize": 30,
        "final_outro_text": "8-Bit Fun with ClipOpera!",
    },
    "retro_16bit_ad": {
        "video_duration": 30,
        "placeholder_url": "https://example.com/retro_16bit_ad.mp4",
        "model_intro_duration": 0,
        "outro_duration": 2,
        "text_fontsize": 36,
        "final_outro_text": "Level Up Your Ads!",
    },
    "retro_32bit_ad": {
        "video_duration": 30,
        "placeholder_url": "https://example.com/retro_32bit_ad.mp4",
        "model_intro_duration": 0,
        "outro_duration": 2,
        "text_fontsize": 42,
        "final_outro_text": "Experience Retro Power!",
    },
}

@retry(**retry_config)
async def safe_get(url: str) -> httpx.Response:
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp

@retry(**retry_config)
async def safe_s3_upload(fileobj, key: str, content_type: str):
    await asyncio.to_thread(
        s3_client.upload_fileobj,
        fileobj,
        S3_BUCKET_NAME,
        key,
        ExtraArgs={"ContentType": content_type, "ACL": "public-read"},
    )


class VideoScene(BaseModel):
    image_url: Optional[str] = None
    text: Optional[str] = None
    duration: float = Field(..., gt=0)
    tts_text: Optional[str] = None

class VideoInput(BaseModel):
    scenes: List[VideoScene]
    width: int = 720
    height: int = 1280
    fps: int = 30
    template_id: str = "standard"
    model_url: Optional[str] = None

class MetaAdInput(BaseModel):
    user_id: str
    ad_account_id: str
    page_id: str
    headline: str
    body: str
    link_url: str
    cta: str = "LEARN_MORE"
    image_hash: Optional[str] = None
    video_id: Optional[str] = None
    campaign_id: Optional[str] = None
    campaign_name: Optional[str] = None
    adset_id: Optional[str] = None
    adset_name: Optional[str] = None
    daily_budget: int = 1000
    objective: str = "LINK_CLICKS"

class CampaignConfigInput(BaseModel):
    user_id: str
    ad_account_id: str
    page_id: str
    headline: str
    body: str
    link_url: str
    cta: str = "LEARN_MORE"
    asset_url: str
    asset_type: str = Field("video", pattern=r"^(video|image)$")
    daily_budget: int = 1000
    objective: str = "LINK_CLICKS"
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    campaign_id: Optional[str] = None
    campaign_name: Optional[str] = None
    adset_id: Optional[str] = None
    adset_name: Optional[str] = None
    access_token: Optional[str] = None


# ---------------------------------------------------------------------------
# 3D MODEL RENDERING MOCK
# ---------------------------------------------------------------------------
async def request_3d_model_render(model_url: str, animation_type: str = "turntable") -> str:
    """Return a placeholder video URL representing a rendered 3D model."""
    logger.info(f"[3D Render Mock] Requesting {animation_type} render for model: {model_url}")
    await asyncio.sleep(2)
    mock_render_url = os.getenv("MOCK_RENDERED_3D_VIDEO_URL", "https://example.com/rendered_3d_model_placeholder.mp4")
    if mock_render_url == "https://example.com/rendered_3d_model_placeholder.mp4":
        logger.warning("MOCK_RENDERED_3D_VIDEO_URL not set. Using generic placeholder.")
    logger.info(f"[3D Render Mock] Returning mocked render URL: {mock_render_url}")
    return mock_render_url


async def generate_video_async(data: VideoInput) -> str:
    cfg = VIDEO_TEMPLATE_CONFIGS.get(data.template_id, {})
    placeholder = cfg.get("placeholder_url")
    if placeholder:
        logger.info(f"[{data.template_id}] Using template-specific placeholder video: {placeholder}")
        return placeholder

    clips = []
    audio_clips = []
    temp_files = []

    if getattr(data, "model_url", None) and cfg.get("model_intro_duration", 0) > 0:
        try:
            rendered_url = await request_3d_model_render(data.model_url)
            model_video_resp = await safe_get(rendered_url)
            tmp_model_video = NamedTemporaryFile(delete=False, suffix=".mp4")
            temp_files.append(tmp_model_video.name)
            with open(tmp_model_video.name, "wb") as f:
                f.write(model_video_resp.content)
            model_clip = VideoFileClip(tmp_model_video.name).resize((data.width, data.height))
            model_clip = model_clip.set_duration(cfg.get("model_intro_duration"))
            clips.append(model_clip)
            logger.info("3D model video successfully integrated into final ad.")
        except Exception as e:
            logger.error(f"[3D Render Integration Error] {e}")
    for scene in data.scenes:
        if scene.image_url:
            img_resp = await safe_get(scene.image_url)
            tmp_img = NamedTemporaryFile(delete=False, suffix=".png")
            temp_files.append(tmp_img.name)
            tmp_img.write(img_resp.content)
            tmp_img.flush()
            base = ImageClip(tmp_img.name).set_duration(scene.duration).resize((data.width, data.height))
        else:
            base = ColorClip(size=(data.width, data.height), color=(0,0,0)).set_duration(scene.duration)
        overlays = [base]
        if scene.text:
            txt_clip = TextClip(scene.text, fontsize=48, color="white").set_position("center").set_duration(scene.duration)
            overlays.append(txt_clip)
        comp = CompositeVideoClip(overlays)
        if scene.tts_text:
            tts = gTTS(scene.tts_text)
            tmp_audio = NamedTemporaryFile(delete=False, suffix=".mp3")
            temp_files.append(tmp_audio.name)
            tts.save(tmp_audio.name)
            audio = AudioFileClip(tmp_audio.name).set_duration(scene.duration)
            comp = comp.set_audio(audio)
            audio_clips.append(audio)
        clips.append(comp)

    outro_duration = cfg.get("outro_duration", 2)
    outro_clip = ColorClip(size=(data.width, data.height), color=(0,0,0)).set_duration(outro_duration)
    outro_text_clip = TextClip(cfg.get("final_outro_text", "Visit our website!"), fontsize=cfg.get("text_fontsize", 48), color="white").set_position("center").set_duration(outro_duration)
    final_outro = CompositeVideoClip([outro_clip, outro_text_clip])
    clips.append(final_outro)
    final_video = concatenate_videoclips(clips, method="compose")
    fixed_total_duration = cfg.get("video_duration")
    if fixed_total_duration:
        if final_video.duration > fixed_total_duration:
            final_video = final_video.subclip(0, fixed_total_duration)
            logger.info(f"Video trimmed to {fixed_total_duration}s.")
        elif final_video.duration < fixed_total_duration:
            pad = ColorClip(size=(data.width, data.height), color=(0,0,0), duration=fixed_total_duration - final_video.duration)
            final_video = concatenate_videoclips([final_video, pad], method="compose")
            logger.info(f"Video extended to {fixed_total_duration}s with filler.")
    if audio_clips:
        final_audio = concatenate_audioclips(audio_clips)
        if fixed_total_duration:
            if final_audio.duration > final_video.duration:
                final_audio = final_audio.subclip(0, final_video.duration)
            elif final_audio.duration < final_video.duration:
                final_audio = final_audio.fx(vfx.loop, duration=final_video.duration)
        final_video = final_video.set_audio(final_audio)
    out_file = NamedTemporaryFile(delete=False, suffix=".mp4")
    temp_files.append(out_file.name)
    final_video.write_videofile(out_file.name, fps=data.fps, codec="libx264", audio_codec="aac")
    try:
        with open(out_file.name, "rb") as f:
            key = f"generated_videos/{uuid.uuid4()}.mp4"
            await safe_s3_upload(f, key, "video/mp4")
        return f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{key}"
    finally:
        for p in temp_files:
            try:
                os.unlink(p)
            except OSError:
                pass

async def create_meta_ad_async(data: MetaAdInput) -> dict:
    token = data.user_id  # For demo we treat user_id as token key
    FacebookAdsApi.init(access_token=token)
    account = AdAccount(f"act_{data.ad_account_id}")
    campaign_id = data.campaign_id
    if not campaign_id:
        campaign = account.create_campaign(params={
            Campaign.Field.name: data.campaign_name or "Generated Campaign",
            Campaign.Field.status: Campaign.Status.paused,
            Campaign.Field.objective: data.objective,
        })
        campaign_id = campaign[Campaign.Field.id]
    adset_id = data.adset_id
    if not adset_id:
        adset = account.create_ad_set(params={
            AdSet.Field.name: data.adset_name or "Generated Ad Set",
            AdSet.Field.campaign_id: campaign_id,
            AdSet.Field.daily_budget: str(data.daily_budget),
            AdSet.Field.billing_event: AdSet.BillingEvent.impressions,
            AdSet.Field.optimization_goal: AdSet.OptimizationGoal.link_clicks,
            AdSet.Field.targeting: {"geo_locations": {"countries": ["US"]}},
            AdSet.Field.status: AdSet.Status.paused,
        })
        adset_id = adset[AdSet.Field.id]
    creative_spec = {
        "page_id": data.page_id,
        "link_data": {
            "message": data.body,
            "link": data.link_url,
            "call_to_action": {"type": data.cta},
            "name": data.headline,
        },
    }
    if data.image_hash:
        creative_spec["link_data"]["image_hash"] = data.image_hash
    if data.video_id:
        creative_spec["video_data"] = {"video_id": data.video_id}
    creative = account.create_ad_creative(params={
        AdCreative.Field.name: "Generated Creative",
        AdCreative.Field.object_story_spec: creative_spec,
    })
    ad = account.create_ad(params={
        Ad.Field.name: "Generated Ad",
        Ad.Field.adset_id: adset_id,
        Ad.Field.creative: {"creative_id": creative[AdCreative.Field.id]},
        Ad.Field.status: Ad.Status.paused,
    })
    return {"ad_id": ad[Ad.Field.id], "campaign_id": campaign_id, "adset_id": adset_id}


async def publish_meta_ad_async(cfg: CampaignConfigInput) -> dict:
    """Upload an asset and create a scheduled ad."""
    token = cfg.access_token
    FacebookAdsApi.init(access_token=token)
    account = AdAccount(f"act_{cfg.ad_account_id}")

    camp_id = cfg.campaign_id
    if not camp_id:
        campaign = account.create_campaign(params={
            Campaign.Field.name: cfg.campaign_name or "Generated Campaign",
            Campaign.Field.status: Campaign.Status.paused,
            Campaign.Field.objective: cfg.objective,
        })
        camp_id = campaign[Campaign.Field.id]

    adset_id = cfg.adset_id
    if not adset_id:
        params = {
            AdSet.Field.name: cfg.adset_name or "Generated Ad Set",
            AdSet.Field.campaign_id: camp_id,
            AdSet.Field.daily_budget: str(cfg.daily_budget),
            AdSet.Field.billing_event: AdSet.BillingEvent.impressions,
            AdSet.Field.optimization_goal: AdSet.OptimizationGoal.link_clicks,
            AdSet.Field.targeting: {"geo_locations": {"countries": ["US"]}},
            AdSet.Field.status: AdSet.Status.paused,
        }
        if cfg.start_time:
            params[AdSet.Field.start_time] = int(cfg.start_time.timestamp())
        if cfg.end_time:
            params[AdSet.Field.end_time] = int(cfg.end_time.timestamp())
        adset = account.create_ad_set(params=params)
        adset_id = adset[AdSet.Field.id]

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(cfg.asset_url)
        resp.raise_for_status()
        suffix = ".mp4" if cfg.asset_type == "video" else ".png"
        tmp = NamedTemporaryFile(delete=False, suffix=suffix)
        tmp.write(resp.content)
        tmp.flush()

    if cfg.asset_type == "video":
        video = AdVideo(parent_id=account.get_id())
        video[AdVideo.Field.filename] = tmp.name
        video.remote_create()
        asset_ref = {"video_id": video[AdVideo.Field.id]}
    else:
        ad_image = AdImage(parent_id=account.get_id())
        ad_image[AdImage.Field.filename] = tmp.name
        ad_image.remote_create()
        asset_ref = {"image_hash": ad_image[AdImage.Field.hash]}
    os.unlink(tmp.name)

    creative_spec = {
        "page_id": cfg.page_id,
        "link_data": {
            "message": cfg.body,
            "link": cfg.link_url,
            "call_to_action": {"type": cfg.cta},
            "name": cfg.headline,
        },
    }
    if cfg.asset_type == "video":
        creative_spec["video_data"] = asset_ref
    else:
        creative_spec["link_data"].update(asset_ref)

    creative = account.create_ad_creative(params={
        AdCreative.Field.name: "Generated Creative",
        AdCreative.Field.object_story_spec: creative_spec,
    })
    ad = account.create_ad(params={
        Ad.Field.name: "Generated Ad",
        Ad.Field.adset_id: adset_id,
        Ad.Field.creative: {"creative_id": creative[AdCreative.Field.id]},
        Ad.Field.status: Ad.Status.paused,
    })
    return {"ad_id": ad[Ad.Field.id], "campaign_id": camp_id, "adset_id": adset_id}


@celery_app.task(name="generate_video_task")
def generate_video_task(data: dict) -> str:
    """Background task to create a video from scene definitions."""
    inp = VideoInput(**data)
    return asyncio.run(generate_video_async(inp))

@celery_app.task(name="create_meta_ad_task")
def create_meta_ad_task(data: dict) -> dict:
    """Background task to create a Meta ad campaign and creative."""
    inp = MetaAdInput(**data)
    return asyncio.run(create_meta_ad_async(inp))


@celery_app.task(name="publish_meta_ad_task")
def publish_meta_ad_task(data: dict) -> dict:
    """Background task to upload an asset and create a scheduled Meta ad."""
    inp = CampaignConfigInput(**data)
    return asyncio.run(publish_meta_ad_async(inp))
