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

It posts the example images to the GLAM API and prints the result URL.

Serverless usage is configured in `api/glam_tryon.py` for Vercel. The `render.yaml` file defines deployment settings for Render.
