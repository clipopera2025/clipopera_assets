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
    "standard": {"video_duration": 30},
    "fast_paced": {"video_duration": 15},
    "luxury_showcase": {"video_duration": 30},
    "explainer": {"video_duration": 60},
    "anime_10s": {
        "video_duration": 10,
        "placeholder_url": "https://example.com/anime_10s.mp4",
    },
    "anime_30s": {
        "video_duration": 30,
        "placeholder_url": "https://example.com/anime_30s.mp4",
    },
    "anime_60s": {
        "video_duration": 60,
        "placeholder_url": "https://example.com/anime_60s.mp4",
    },
    "ascii_art_ad": {
        "video_duration": 30,
        "placeholder_url": "https://example.com/ascii_art_ad.mp4",
    },
    "retro_8bit_ad": {
        "video_duration": 30,
        "placeholder_url": "https://example.com/retro_8bit_ad.mp4",
    },
    "retro_16bit_ad": {
        "video_duration": 30,
        "placeholder_url": "https://example.com/retro_16bit_ad.mp4",
    },
    "retro_32bit_ad": {
        "video_duration": 30,
        "placeholder_url": "https://example.com/retro_32bit_ad.mp4",
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


async def generate_video_async(data: VideoInput) -> str:
    cfg = VIDEO_TEMPLATE_CONFIGS.get(data.template_id, {})
    placeholder = cfg.get("placeholder_url")
    if placeholder:
        return placeholder

    clips = []
    audio_clips = []
    temp_files = []
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
    final_video = concatenate_videoclips(clips, method="compose")
    target_duration = cfg.get("video_duration")
    if target_duration:
        if final_video.duration > target_duration:
            final_video = final_video.subclip(0, target_duration)
        elif final_video.duration < target_duration:
            pad = ColorClip(size=(data.width, data.height), color=(0,0,0), duration=target_duration - final_video.duration)
            final_video = concatenate_videoclips([final_video, pad], method="compose")
    if audio_clips:
        final_audio = concatenate_audioclips(audio_clips)
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
