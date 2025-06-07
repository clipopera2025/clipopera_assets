import os
import sys
import requests

NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
NOTION_PAGE_ID = os.environ.get("NOTION_PAGE_ID")
NOTION_VERSION = "2022-06-28"

if not NOTION_TOKEN or not NOTION_PAGE_ID:
    sys.exit("NOTION_TOKEN and NOTION_PAGE_ID environment variables are required")

if len(sys.argv) < 3:
    sys.exit("Usage: python send_to_notion.py <markdown_file> <page_title>")

md_path = sys.argv[1]
page_title = sys.argv[2]

with open(md_path, "r", encoding="utf-8") as f:
    content = f.read()

url = "https://api.notion.com/v1/pages"
headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": NOTION_VERSION,
    "Content-Type": "application/json",
}

payload = {
    "parent": {"page_id": NOTION_PAGE_ID},
    "properties": {
        "title": {
            "title": [
                {"type": "text", "text": {"content": page_title}}
            ]
        }
    },
    "children": [
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {"type": "text", "text": {"content": content}}
                ]
            }
        }
    ]
}

response = requests.post(url, json=payload, headers=headers)

if response.status_code != 200:
    print(response.text)
    sys.exit(f"Failed to create page: {response.status_code}")

print(f"Page created: {response.json().get('url')}")
