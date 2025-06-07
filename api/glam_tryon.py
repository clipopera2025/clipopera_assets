from http.server import BaseHTTPRequestHandler
import requests
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        media_url = "https://images.squarespace-cdn.com/..."
        garment_url = "https://images.squarespace-cdn.com/..."
        glam_api_key = "BkhUMHs-bSJRtW9VSROlsw"

        headers = {
            "Content-Type": "application/json",
            "X-API-Key": glam_api_key
        }

        payload = {
            "mask_type": "overall",
            "media_url": media_url,
            "garment_url": garment_url
        }

        r = requests.post("https://api.glam.ai/api/v1/tryon", headers=headers, json=payload)

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(r.content)
