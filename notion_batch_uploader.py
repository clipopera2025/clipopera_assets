import os
import sys
import requests
import re

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("NOTION_PAGE_ID")
NOTION_VERSION = "2022-06-28"

if not NOTION_TOKEN or not DATABASE_ID:
    sys.exit("NOTION_TOKEN and NOTION_PAGE_ID environment variables are required")

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": NOTION_VERSION,
    "Content-Type": "application/json",
}

# Determine markdown files to upload
md_files = [f for f in os.listdir('.') if f.endswith('.md')]

for md_path in md_files:
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    filename = os.path.basename(md_path)
    tags = []
    topics = []
    quote = ""

    for line in content.splitlines():
        if line.lower().startswith("**tags:**") or line.lower().startswith("tags:"):
            line_tags = line.split(':', 1)[1]
            tags = [t.strip().strip('#') for t in re.split('[, ]', line_tags) if t.strip()]
        if line.lower().startswith("**topics:**") or line.lower().startswith("topics:"):
            line_topics = line.split(':', 1)[1]
            topics = [t.strip() for t in re.split('[,]', line_topics) if t.strip()]

    if "### Quote" in content:
        after_quote = content.split("### Quote", 1)[1]
        first_line = after_quote.strip().splitlines()[0]
        quote = first_line.strip('"')

    properties = {
        "Name": {"title": [{"text": {"content": filename}}]}
    }
    if tags:
        properties["Tags"] = {"multi_select": [{"name": t} for t in tags]}
    if topics:
        properties["Topics"] = {"multi_select": [{"name": t} for t in topics]}
    if quote:
        properties["Quote"] = {"rich_text": [{"text": {"content": quote}}]}

    payload = {
        "parent": {"database_id": DATABASE_ID},
        "properties": properties,
        "children": [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": content}}]
                }
            }
        ]
    }

    resp = requests.post("https://api.notion.com/v1/pages", headers=headers, json=payload)
    if resp.status_code != 200:
        print(resp.text)
        print(f"Failed to create page for {md_path}: {resp.status_code}")
    else:
        print(f"Uploaded {md_path} -> {resp.json().get('url')}")
