# clipopera_assets
This repository contains assets and scripts used for ClipOpera projects.

## Notion to Discord Script

`scripts/notion_to_discord.js` fetches new entries from a Notion database and posts them to a Discord channel. If configured, uploaded media is stored in a Google Drive folder and the share link is included in the Discord message.

### Setup

1. Install dependencies using npm:
   ```bash
   npm install
   ```
2. Create a `.env` file in the repository root with the following variables (this file is ignored by Git; ensure `.gitignore` contains `.env`):
   ```ini
   NOTION_TOKEN=<your_notional_integration_token>
   NOTION_DATABASE_ID=<the database ID>
   DISCORD_WEBHOOK_URL=<your Discord webhook>
   # optional
   GDRIVE_FOLDER_ID=<your Google Drive folder ID>
   ```

### Running the Script

Execute the script with Node:

```bash
node scripts/notion_to_discord.js
```

The script will query the Notion database for entries where the `Status` property equals `New`, send the contents to Discord, and upload any attached file to Google Drive if a folder ID is provided.

## ClipOpera Ad Generator

`clipopera_ad_generator.html` is a simple in-browser tool for previewing images or videos and exporting a short GIF or MP4. Open the file in your browser, choose a fit mode, upload media, then export the result.

## FastAPI Ad Generation API

The `main.py` application exposes endpoints for generating ad copy, images and videos.

### Setup

1. Install Python dependencies (includes `httpx`, `tenacity`, and `python-jose` for JWT auth):
   ```bash
   pip install -r requirements.txt
   # ffmpeg is required for video generation
   # e.g. on Ubuntu: sudo apt-get install ffmpeg
   # Redis is required for Celery task queues
   # e.g. on Ubuntu: sudo apt-get install redis-server
   ```
2. Configure a `.env` file with the following variables:
   ```ini
   GEMINI_API_KEY=<google_api_key>
   OPENAI_API_KEY=<openai_api_key>
   AWS_ACCESS_KEY_ID=<aws_access_key>
   AWS_SECRET_ACCESS_KEY=<aws_secret_key>
   AWS_REGION=<aws_region>
   S3_BUCKET_NAME=<your_s3_bucket>
   META_APP_ID=<meta_app_id>
   META_APP_SECRET=<meta_app_secret>
   META_REDIRECT_URI=<https://yourdomain.com/meta/callback>
   CELERY_BROKER_URL=redis://localhost:6379/0
   SECRET_KEY=<random_secret_key>
   DEMO_USERNAME=<demo_username>
   DEMO_PASSWORD=<demo_password>
   # used by the video generation task for a mock 3D render clip
   MOCK_RENDERED_3D_VIDEO_URL=<https://your-bucket.s3.amazonaws.com/mock_render.mp4>
   ANIME_10S_PLACEHOLDER_URL=<https://your-bucket.s3.amazonaws.com/anime10.mp4>
   ANIME_30S_PLACEHOLDER_URL=<https://your-bucket.s3.amazonaws.com/anime30.mp4>
   ANIME_60S_PLACEHOLDER_URL=<https://your-bucket.s3.amazonaws.com/anime60.mp4>
   ASCII_AD_PLACEHOLDER_URL=<https://your-bucket.s3.amazonaws.com/ascii.mp4>
   RETRO_8BIT_AD_PLACEHOLDER_URL=<https://your-bucket.s3.amazonaws.com/8bit.mp4>
   RETRO_16BIT_AD_PLACEHOLDER_URL=<https://your-bucket.s3.amazonaws.com/16bit.mp4>
   RETRO_32BIT_AD_PLACEHOLDER_URL=<https://your-bucket.s3.amazonaws.com/32bit.mp4>
  ```
   These variables are loaded at runtime using `python-dotenv`.

### Uploading Placeholder Videos
Place your placeholder .mp4 files in a `placeholders/` folder at the project root and run:
```bash
python scripts/upload_placeholders_to_s3.py
```
The script uploads each video to your configured S3 bucket and prints its public URL.

### Running

Launch the server with Uvicorn:

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

Visit `http://localhost:8000/docs` for interactive Swagger docs.

The image endpoint accepts a `quality` field (`standard` or `hd`) controlling
the fidelity and cost of DALL-E generation.

To process requests, run a Celery worker in a separate terminal:

```bash
celery -A celery_worker.celery_app worker --loglevel=info
```
Ensure the worker environment also has AWS and related credentials configured.
The following variables are required when running the worker:

```ini
AWS_ACCESS_KEY_ID=<aws_access_key>
AWS_SECRET_ACCESS_KEY=<aws_secret_key>
AWS_REGION=<aws_region>
S3_BUCKET_NAME=<s3_bucket>
OPENAI_API_KEY=<openai_key>
GEMINI_API_KEY=<gemini_key>
MOCK_RENDERED_3D_VIDEO_URL=<https://your-bucket.s3.amazonaws.com/mock_render.mp4>
```

Without these the worker will exit on start-up because it cannot upload
generated media to S3 or call the generative APIs.

The API exposes several endpoints. Video and Meta ad creation run asynchronously and return a `task_id` which can be polled via `/api/v1/tasks/{task_id}`:

* `POST /api/v1/generate/ad_copy` – generate marketing copy
* `POST /api/v1/generate/image` – create an image via DALL‑E 3 and return an S3 URL
* `POST /api/v1/upload` – upload a user file to S3 and return a URL
* `POST /api/v1/generate/video` – assemble short videos from scenes
* `GET /api/v1/platforms/meta/auth_start` – begin Meta OAuth flow
* `GET /api/v1/platforms/meta/oauth_callback` – handle Meta redirect
* `POST /api/v1/platforms/meta/upload/image` – upload an image to Meta Ads
* `POST /api/v1/platforms/meta/upload/video` – upload a video to Meta Ads
* `POST /api/v1/platforms/meta/create_ad` – create a basic ad campaign and ad
* `POST /api/v1/platforms/meta/publish_ad` – publish a scheduled ad campaign
* `GET /api/v1/tasks/{task_id}` – fetch task status and result
* `POST /token` – obtain a JWT access token
* `POST /register` – create a new user account
* `GET /meta-status` – check if the current user linked a Meta account
* `POST /upload-model` – upload a 3D model file (authenticated)
* `GET /models` – list uploaded model URLs (authenticated)

### Demo React Frontend

The `frontend` directory contains a simple React app showcasing how to interact
with the API. It supports logging in, uploading 3D models and linking a Meta
account. To run the demo:

```bash
cd frontend
npm install
npm start
```

The app is intentionally minimal and meant only as an example of integrating the
ClipOpera API into a frontend project. The Button component used in the demo is exported as the default from `frontend/components/ui/button.js`, so import it without braces.
The template dropdown now includes anime cartoon presets (10, 30 and 60 second ads) as well as experimental ASCII art and retro 8/16/32-bit styles. All of these currently output placeholder videos.

### Health Check

A `/health` endpoint returns `{ "status": "ok" }` for uptime monitoring.
Run `curl http://localhost:8000/health` to check.

## Node.js Upload & Meta OAuth Demo

This repo includes a small Express server located in `node_demo/` demonstrating file uploads to AWS S3 and a basic Meta OAuth flow.

Install dependencies and run:

```bash
cd node_demo
npm install
npm start
npm test         # runs a simple placeholder test script
```

Then visit `http://localhost:3000` to try uploading a file or initiating Meta login.

## Avatar Page Demo

Run a small Express server that serves the CL-0 avatar page:

```bash
cd node_demo
npm install          # if not already done
npm run start-avatar
```

Open `http://localhost:4000` in your browser to see the interactive avatar.
