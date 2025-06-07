# clipopera_assets

This repository stores 3D assets and a demo GLAM try-on script.

## Setup

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Run the local try-on script:

```bash
python glam_tryon.py
```

It posts the example images to the GLAM API and prints the result URL. Set
`GLAM_API_KEY` in your environment or `.env` file before running.

Serverless usage is provided in `api/glam_tryon.py` as an example. The `render.yaml` file defines deployment settings for Render.

## 📤 ClipOpera Notion Upload Guide

Use the `create_notion_page.py` script to send project data to your Notion workspace.

### ✅ Environment Setup

Make sure you’ve defined the following in your `.env` file:

```dotenv
NOTION_TOKEN=your-secret-token
NOTION_DATABASE_ID=your-notion-database-id
GLAM_API_KEY=your-glam-key-here
```

You can also set these as environment variables directly.

### 🚀 Run the Notion Script

From the root of your project:

```bash
python create_notion_page.py \
  --project "ClipOpera AI Portal" \
  --status "In Progress" \
  --link "https://clipopera.com" \
  --budget 2500 \
  --drive "https://drive.google.com/drive/folders/your-folder-id" \
  --webmaster "GPT-Webmaster" \
  --codex "PenAI Assistant" \
  --gpts "clipbot_id,jetmode_ai" \
  --library "/path/to/gpt_library" \
  --registry "/path/to/models.json"
```

### 📡 API Usage (Optional)

You can also POST to the Flask server if it’s running:

```bash
curl -X POST http://localhost:5000/run-script \
  -H "Content-Type: application/json" \
  -d '{
    "project": "ClipOpera AI Portal",
    "status": "Queued",
    "link": "https://clipopera.com",
    "drive": "https://drive.google.com/...",
    "budget": 2500
  }'
```

### 🧪 Testing

```bash
python -m py_compile create_notion_page.py glam_tryon.py api/glam_tryon.py
```

```bash
black --check create_notion_page.py glam_tryon.py api/glam_tryon.py
```

> ❗ Make sure your environment variables are set before running these scripts.

Need help setting up your Notion integration? Let me know!
