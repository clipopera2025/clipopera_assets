import os
import argparse
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("NOTION_TOKEN")
notion = Client(auth=token)


def create_page(
    project: str,
    status: str,
    link: str,
    budget: float,
    drive: str | None = None,
    webmaster: str | None = None,
    codex: str | None = None,
    sora: str | None = None,
    gpts: str | None = None,
    library: str | None = None,
    registry: str | None = None,
) -> None:
    """Create a task page in the configured Notion database."""
    database_id = os.getenv("NOTION_DATABASE_ID")
    if not token or not database_id:
        raise RuntimeError(
            "NOTION_TOKEN and NOTION_DATABASE_ID must be set either in the .env file "
            "or as environment variables"
        )

    properties = {
        "Project": {"title": [{"text": {"content": project}}]},
        "Status": {"select": {"name": status}},
        "Link": {"url": link},
        "Budget": {"number": float(budget)},
    }

    if drive:
        properties["Drive"] = {"url": drive}
    if webmaster:
        properties["Webmaster"] = {"rich_text": [{"text": {"content": webmaster}}]}
    if codex:
        properties["Codex"] = {"rich_text": [{"text": {"content": codex}}]}
    if sora:
        properties["Sora"] = {"rich_text": [{"text": {"content": sora}}]}
    if gpts:
        properties["GPTs"] = {"rich_text": [{"text": {"content": gpts}}]}
    if library:
        properties["Library"] = {"rich_text": [{"text": {"content": library}}]}
    if registry:
        properties["Registry"] = {"rich_text": [{"text": {"content": registry}}]}

    notion.pages.create(parent={"database_id": database_id}, properties=properties)


def main():
    parser = argparse.ArgumentParser(description="Create a Notion page")
    parser.add_argument("--project", required=True, help="Project name")
    parser.add_argument("--status", required=True, help="Status column")
    parser.add_argument("--link", required=True, help="Link column")
    parser.add_argument(
        "--budget",
        type=float,
        required=True,
        help="Budget amount",
    )
    parser.add_argument("--drive", help="Google Drive folder link")
    parser.add_argument("--webmaster", help="Webmaster name")
    parser.add_argument("--codex", help="Codex identifier")
    parser.add_argument("--sora", help="Sora sync info")
    parser.add_argument("--gpts", help="Comma-separated GPT identifiers")
    parser.add_argument("--library", help="Path to GPT library")
    parser.add_argument("--registry", help="Path to GPT registry")
    args = parser.parse_args()

    create_page(
        args.project,
        args.status,
        args.link,
        args.budget,
        drive=args.drive,
        webmaster=args.webmaster,
        codex=args.codex,
        sora=args.sora,
        gpts=args.gpts,
        library=args.library,
        registry=args.registry,
    )


if __name__ == "__main__":
    main()
