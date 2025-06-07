import os
from http.server import BaseHTTPRequestHandler

import requests

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = lambda: None


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        media_url = "https://images.squarespace-cdn.com/..."
        garment_url = "https://images.squarespace-cdn.com/..."
        load_dotenv()
        glam_api_key = os.getenv("GLAM_API_KEY")
        if not glam_api_key:
            self.send_error(500, "GLAM_API_KEY must be set")
            return

        headers = {"Content-Type": "application/json", "X-API-Key": glam_api_key}

        payload = {
            "mask_type": "overall",
            "media_url": media_url,
            "garment_url": garment_url,
        }

        r = requests.post(
            "https://api.glam.ai/api/v1/tryon", headers=headers, json=payload
        )

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(r.content)
