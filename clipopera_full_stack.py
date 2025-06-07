# clipopera_full_stack.py

import os
import argparse
from dotenv import load_dotenv
from notion_client import Client as NotionClient
import openai
import requests

# Load .env
load_dotenv()

# Notion & OpenAI init
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SORA_API_KEY = os.getenv("SORA_API_KEY")

notion = NotionClient(auth=NOTION_TOKEN)
openai.api_key = OPENAI_API_KEY


def create_notion_database():
    print("\U0001f4c1 Creating Notion DB structure...")
    db = notion.databases.create(
        parent={"type": "page_id", "page_id": os.getenv("NOTION_PARENT_PAGE_ID")},
        title=[{"type": "text", "text": {"content": "\U0001f3ac ClipOpera Projects"}}],
        properties={
            "Project": {"title": {}},
            "Status": {
                "select": {
                    "options": [
                        {"name": "In Production", "color": "yellow"},
                        {"name": "In Queue", "color": "blue"},
                        {"name": "Complete", "color": "green"},
                    ]
                }
            },
            "Link": {"url": {}},
            "Budget": {"number": {"format": "dollar"}},
            "Drive Link": {"url": {}},
            "Webmaster": {"rich_text": {}},
            "Codex Assistant": {"rich_text": {}},
        },
    )
    print("✅ Created:", db["id"])
    return db["id"]


def create_project_page(project, status, link, budget, drive, webmaster, codex):
    print(f"\U0001f680 Creating Notion project: {project}")
    notion.pages.create(
        parent={"database_id": NOTION_DATABASE_ID},
        properties={
            "Project": {"title": [{"text": {"content": project}}]},
            "Status": {"select": {"name": status}},
            "Link": {"url": link},
            "Budget": {"number": float(budget)},
            "Drive Link": {"url": drive},
            "Webmaster": {"rich_text": [{"text": {"content": webmaster}}]},
            "Codex Assistant": {"rich_text": [{"text": {"content": codex}}]},
        },
    )
    print("✅ Project logged in Notion.")


def trigger_gpt_actions(gpt_ids):
    print("\U0001f916 Triggering GPT logic...")
    for gpt_id in gpt_ids.split(","):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": f"You are {gpt_id}"},
                    {
                        "role": "user",
                        "content": "Generate production notes for ClipOpera project.",
                    },
                ],
            )
            print(
                f"\U0001f4c4 {gpt_id} output:\n", response.choices[0].message["content"]
            )
        except Exception as e:
            print(f"⚠️ GPT failure for {gpt_id}: {e}")


def sync_with_sora(project, status, link, drive, gpts):
    print("\U0001f4e1 Syncing with Sora...")
    try:
        requests.post(
            "https://api.sora.ai/sync",
            headers={"Authorization": f"Bearer {SORA_API_KEY}"},
            json={
                "project": project,
                "status": status,
                "link": link,
                "drive": drive,
                "gpts": gpts.split(","),
            },
        )
        print("✅ Sora synced.")
    except Exception as e:
        print("❌ Sora sync failed:", e)


def codex_autocommand(codex_name, project, status):
    print(f"\U0001f9e0 Codex '{codex_name}' is analyzing...")
    if codex_name == "PenAI Assistant":
        print(
            f"\U0001f4e8 PenAI routing editing instructions for: {project} ({status})"
        )
    else:
        print("⚠️ No codex autocommand defined.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("--status", required=True)
    parser.add_argument("--link", required=True)
    parser.add_argument("--budget", required=True)
    parser.add_argument("--drive", required=True)
    parser.add_argument("--webmaster", required=True)
    parser.add_argument("--codex", required=True)
    parser.add_argument("--gpts", default="")
    parser.add_argument("--sora", action="store_true")
    parser.add_argument("--create_db", action="store_true")

    args = parser.parse_args()

    if args.create_db:
        create_notion_database()

    create_project_page(
        args.project,
        args.status,
        args.link,
        args.budget,
        args.drive,
        args.webmaster,
        args.codex,
    )

    if args.gpts:
        trigger_gpt_actions(args.gpts)

    codex_autocommand(args.codex, args.project, args.status)

    if args.sora:
        sync_with_sora(args.project, args.status, args.link, args.drive, args.gpts)
