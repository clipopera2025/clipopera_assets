from __future__ import annotations
import os
import argparse
from typing import Dict

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - fallback if python-dotenv not installed
    load_dotenv = lambda: None  # type: ignore

try:
    from notion_client import Client
except ImportError:  # pragma: no cover - ensures helpful error if dependency missing
    Client = None  # type: ignore


def build_properties(args: argparse.Namespace) -> Dict[str, dict]:
    props: Dict[str, dict] = {
        "Name": {"title": [{"text": {"content": args.project}}]},
        "Status": {"rich_text": [{"text": {"content": args.status}}]},
        "Link": {"url": args.link},
        "Budget": {"number": args.budget},
    }
    if args.drive:
        props["Drive"] = {"url": args.drive}
    if args.webmaster:
        props["Webmaster"] = {"rich_text": [{"text": {"content": args.webmaster}}]}
    if args.codex:
        props["Codex"] = {"rich_text": [{"text": {"content": args.codex}}]}
    if args.gpts:
        props["GPTs"] = {"rich_text": [{"text": {"content": args.gpts}}]}
    if args.library:
        props["Library"] = {"rich_text": [{"text": {"content": args.library}}]}
    if args.registry:
        props["Registry"] = {"rich_text": [{"text": {"content": args.registry}}]}
    return props


def main() -> None:
    load_dotenv()
    token = os.getenv("NOTION_TOKEN")
    db_id = os.getenv("NOTION_DATABASE_ID")
    if not token or not db_id:
        raise EnvironmentError("NOTION_TOKEN and NOTION_DATABASE_ID must be set")

    parser = argparse.ArgumentParser(description="Create a Notion project page")
    parser.add_argument("--project", required=True, help="Project name")
    parser.add_argument("--status", required=True, help="Current status")
    parser.add_argument("--link", required=True, help="Project link")
    parser.add_argument("--budget", type=int, required=True, help="Budget amount")
    parser.add_argument("--drive", help="Google Drive folder URL")
    parser.add_argument("--webmaster", help="Webmaster name")
    parser.add_argument("--codex", help="Codex assistant")
    parser.add_argument("--gpts", help="Comma-separated GPT IDs")
    parser.add_argument("--library", help="Path to GPT library")
    parser.add_argument("--registry", help="Path to models registry")
    args = parser.parse_args()

    if Client is None:
        raise ImportError("notion-client is required to run this script")

    client = Client(auth=token)
    props = build_properties(args)
    client.pages.create(parent={"database_id": db_id}, properties=props)
    print("Notion page created successfully")


if __name__ == "__main__":
    main()
