import os
import io
import uuid
import logging
import asyncio
from typing import List, Optional
from tempfile import NamedTemporaryFile

from celery import Celery

import httpx
from tenacity import retry, stop_after_attempt, wait_fixed

from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from jose import JWTError, jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv

import google.generativeai as genai
import boto3
from openai import AsyncOpenAI
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adimage import AdImage
from facebook_business.adobjects.advideo import AdVideo

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
META_APP_ID = os.getenv("META_APP_ID")
META_APP_SECRET = os.getenv("META_APP_SECRET")
META_REDIRECT_URI = os.getenv("META_REDIRECT_URI")
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
SECRET_KEY = os.getenv("SECRET_KEY", "change_me")
DEMO_USERNAME = os.getenv("DEMO_USERNAME", "demo")
DEMO_PASSWORD = os.getenv("DEMO_PASSWORD", "password")

# simple in-memory user store for demo purposes
USERS = {DEMO_USERNAME: DEMO_PASSWORD}
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set.")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable not set.")

if not all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, S3_BUCKET_NAME]):
    raise ValueError("AWS credentials or S3 bucket configuration missing.")

openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# simple in-memory storage for Meta user tokens
TOKEN_STORE = {}

# Retry helpers for external services
retry_config = dict(stop=stop_after_attempt(3), wait=wait_fixed(2))

@retry(**retry_config)
async def safe_get(url: str) -> httpx.Response:
    logger.info("Fetching %s", url)
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp

@retry(**retry_config)
async def safe_s3_upload(fileobj, key: str, content_type: str):
    logger.info("Uploading %s to S3", key)
    await asyncio.to_thread(
        s3_client.upload_fileobj,
        fileobj,
        S3_BUCKET_NAME,
        key,
        ExtraArgs={"ContentType": content_type, "ACL": "public-read"},
    )

@retry(**retry_config)
async def safe_dalle(prompt: str, size: str, quality: str):
    logger.info("Generating image via DALL-E")
    return await openai_client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size=size,
        quality=quality,
        n=1,
    )

s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

celery_app = Celery('worker', broker=CELERY_BROKER_URL, backend=CELERY_BROKER_URL)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def authenticate_user(username: str, password: str) -> bool:
    return USERS.get(username) == password

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username not in USERS:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return username

USER_MODELS: dict[str, list] = {}

genai.configure(api_key=GEMINI_API_KEY)

app = FastAPI(
    title="Social Ad Generator API",
    description="API for generating social media ad copy, images, and videos using AI."
)

class AdCopyInput(BaseModel):
    product_name: str
    product_description: str = Field(..., max_length=500)
    target_audience_keywords: Optional[List[str]] = None
    marketing_goal: str
    ad_tone: Optional[str] = None
    num_variations: int = Field(2, ge=1, le=5)

class GeneratedAdCopy(BaseModel):
    headline: str
    body: str
    cta: str

class AdCopyOutput(BaseModel):
    ad_copies: List[GeneratedAdCopy]

class ImageInput(BaseModel):
    prompt: str
    aspect_ratio: str = Field(..., pattern=r"^(1:1|16:9|9:16|4:3|3:2)$")
    style: Optional[str] = None
    branding_elements: Optional[List[str]] = None
    quality: str = Field("standard", pattern=r"^(standard|hd)$")

class ImageOutput(BaseModel):
    image_url: str

class TaskStatus(BaseModel):
    task_id: str

class RegisterInput(BaseModel):
    username: str
    password: str

# Video generation schemas
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

class VideoOutput(BaseModel):
    video_url: str


@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if not authenticate_user(form_data.username, form_data.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    access_token = create_access_token({"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/register")
async def register(user: RegisterInput):
    if user.username in USERS:
        raise HTTPException(status_code=400, detail="User already exists")
    USERS[user.username] = user.password
    return {"message": "registered"}


@app.post("/upload-model")
async def upload_model(file: UploadFile = File(...), current_user: str = Depends(get_current_user)):
    key = f"models/{current_user}/{uuid.uuid4()}_{file.filename}"
    await safe_s3_upload(file.file, key, file.content_type or "application/octet-stream")
    url = f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{key}"
    USER_MODELS.setdefault(current_user, []).append({"id": uuid.uuid4().hex, "name": file.filename, "url": url})
    return {"url": url}


@app.get("/models")
async def list_models(current_user: str = Depends(get_current_user)):
    return USER_MODELS.get(current_user, [])

@app.post("/api/v1/generate/ad_copy", response_model=AdCopyOutput)
async def generate_ad_copy(input: AdCopyInput):
    prompt_parts = [
        "You are an expert social media advertiser.",
        f"Generate {input.num_variations} unique ad copy variations for a product:",
        f"Product Name: {input.product_name}",
        f"Product Description: {input.product_description}",
    ]
    if input.target_audience_keywords:
        prompt_parts.append(f"Target Audience Keywords: {', '.join(input.target_audience_keywords)}")
    if input.marketing_goal:
        prompt_parts.append(f"Marketing Goal: {input.marketing_goal}")
    if input.ad_tone:
        prompt_parts.append(f"Ad Tone: {input.ad_tone}")
    prompt_parts.append(
        "\nFor each variation, provide a concise headline (under 10 words), "
        "engaging body copy (under 50 words), and a clear Call to Action (CTA).\n"
        "Format the output strictly as a JSON array of objects with 'headline', 'body', and 'cta'."
    )
    full_prompt = "\n".join(prompt_parts)

    try:
        model = genai.GenerativeModel('gemini-pro')
        response = await model.generate_content_async(
            full_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                candidate_count=1
            )
        )
        gemini_text_output = response.candidates[0].content.parts[0].text

        import json
        import re
        json_match = re.search(r"```json\n(.*)\n```", gemini_text_output, re.DOTALL)
        json_string = json_match.group(1) if json_match else gemini_text_output.strip()
        generated_data = json.loads(json_string)
        return AdCopyOutput(ad_copies=generated_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ad copy generation error: {str(e)}")

@app.post("/api/v1/generate/image", response_model=ImageOutput)
async def generate_image(input: ImageInput):
    dalle_prompt = input.prompt
    if input.style:
        dalle_prompt += f", in a {input.style} style"
    if input.branding_elements:
        dalle_prompt += f", with {', '.join(input.branding_elements)}"
    size_map = {
        "1:1": "1024x1024",
        "16:9": "1792x1024",
        "9:16": "1024x1792",
        "4:3": "1792x1024",
        "3:2": "1792x1024",
    }
    dalle_size = size_map.get(input.aspect_ratio, "1024x1024")
    try:
        resp = await safe_dalle(dalle_prompt, dalle_size, input.quality)
        url = resp.data[0].url
        img_resp = await safe_get(url)
        image_bytes = io.BytesIO(img_resp.content)
        key = f"generated_ads/{uuid.uuid4()}.png"
        await safe_s3_upload(image_bytes, key, "image/png")
        return ImageOutput(
            image_url=f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{key}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image generation error: {str(e)}")


@app.post("/api/v1/upload", response_model=ImageOutput)
async def upload_file(file: UploadFile = File(...)):
    """Upload a user provided file to S3 and return a public URL."""
    key = f"uploads/{uuid.uuid4()}_{file.filename}"
    try:
        await safe_s3_upload(file.file, key, file.content_type or "application/octet-stream")
        return ImageOutput(image_url=f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{key}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.post("/api/v1/generate/video", response_model=TaskStatus)
async def generate_video(input: VideoInput):
    task = celery_app.send_task("generate_video_task", args=[input.dict()])
    return TaskStatus(task_id=task.id)


# --- Meta Ads API Endpoints ---

@app.get("/api/v1/platforms/meta/auth_start")
async def meta_auth_start(user_id: str):
    if not META_APP_ID or not META_REDIRECT_URI:
        raise HTTPException(status_code=500, detail="Meta app not configured")
    auth_url = (
        "https://www.facebook.com/v18.0/dialog/oauth"
        f"?client_id={META_APP_ID}&redirect_uri={META_REDIRECT_URI}&state={user_id}"
        "&scope=ads_management,business_management"
    )
    return {"auth_url": auth_url}


@app.get("/api/v1/platforms/meta/oauth_callback")
async def meta_oauth_callback(code: str, state: str):
    if not META_APP_ID or not META_APP_SECRET or not META_REDIRECT_URI:
        raise HTTPException(status_code=500, detail="Meta app not configured")
    async with httpx.AsyncClient(timeout=10) as client:
        token_resp = await client.get(
            "https://graph.facebook.com/v18.0/oauth/access_token",
            params={
                "client_id": META_APP_ID,
                "client_secret": META_APP_SECRET,
                "redirect_uri": META_REDIRECT_URI,
                "code": code,
            },
        )
        token_resp.raise_for_status()
        access = token_resp.json().get("access_token")
        ll_resp = await client.get(
            "https://graph.facebook.com/v18.0/oauth/access_token",
            params={
                "grant_type": "fb_exchange_token",
                "client_id": META_APP_ID,
                "client_secret": META_APP_SECRET,
                "fb_exchange_token": access,
            },
        )
        ll_resp.raise_for_status()
        token = ll_resp.json().get("access_token")
        me_resp = await client.get(
            "https://graph.facebook.com/v18.0/me",
            params={"access_token": token},
        )
        me_resp.raise_for_status()
        user_id_fb = me_resp.json().get("id")
    TOKEN_STORE[state] = token
    TOKEN_STORE[state + "_fbid"] = user_id_fb
    return {"meta_user_id": user_id_fb}


@app.get("/meta-status")
async def meta_status(current_user: str = Depends(get_current_user)):
    return {"linked": current_user in TOKEN_STORE}


@app.post("/api/v1/platforms/meta/upload/image")
async def meta_upload_image(user_id: str, ad_account_id: str, image_url: str):
    token = TOKEN_STORE.get(user_id)
    if not token:
        raise HTTPException(status_code=400, detail="User not authorized")
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(image_url)
        resp.raise_for_status()
    with NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        tmp.write(resp.content)
        tmp.flush()
        FacebookAdsApi.init(access_token=token)
        ad_image = AdImage(parent_id=ad_account_id)
        ad_image[AdImage.Field.filename] = tmp.name
        ad_image.remote_create()
    os.unlink(tmp.name)
    return {"image_hash": ad_image[AdImage.Field.hash]}


@app.post("/api/v1/platforms/meta/upload/video")
async def meta_upload_video(user_id: str, ad_account_id: str, video_url: str):
    token = TOKEN_STORE.get(user_id)
    if not token:
        raise HTTPException(status_code=400, detail="User not authorized")
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(video_url)
        resp.raise_for_status()
    with NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
        tmp.write(resp.content)
        tmp.flush()
        FacebookAdsApi.init(access_token=token)
        video = AdVideo(parent_id=ad_account_id)
        video[AdVideo.Field.filename] = tmp.name
        video.remote_create()
        status_url = video[AdVideo.Field.id]
    os.unlink(tmp.name)
    return {"video_id": status_url}


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


@app.post("/api/v1/platforms/meta/create_ad", response_model=TaskStatus)
async def meta_create_ad(input: MetaAdInput):
    task = celery_app.send_task("create_meta_ad_task", args=[input.dict()])
    return TaskStatus(task_id=task.id)


@app.get("/api/v1/tasks/{task_id}")
async def get_task(task_id: str):
    res = celery_app.AsyncResult(task_id)
    if res.state == "PENDING":
        return {"status": "pending"}
    if res.state == "FAILURE":
        return {"status": "failure", "detail": str(res.result)}
    if res.state == "SUCCESS":
        return {"status": "success", "result": res.result}
    return {"status": res.state.lower()}
