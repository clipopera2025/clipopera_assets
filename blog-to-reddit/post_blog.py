"""Post published Notion blog entries to Reddit.

The script fetches the most recently created page whose ``Status`` is
``Published`` and posts it to the configured subreddit. After posting, the page
is marked as ``Posted`` in Notion.
"""

from __future__ import annotations

import os
import logging
from dotenv import load_dotenv
from notion_client import Client
import praw

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(message)s")


def debug_env_vars() -> None:
    """Log whether required environment variables are set."""

    logging.info("🔍 Checking environment variable loading:")
    logging.info("REDDIT_USERNAME: %s", os.getenv("REDDIT_USERNAME"))

    logging.info("🔍 Debugging environment variables:")
    for key in [
        "NOTION_API_KEY",
        "NOTION_DATABASE_ID",
        "REDDIT_CLIENT_ID",
        "REDDIT_CLIENT_SECRET",
        "REDDIT_USERNAME",
        "REDDIT_PASSWORD",
        "REDDIT_SUBREDDIT",
    ]:
        value = os.getenv(key)
        logging.info("%s: %s", key, "✅ SET" if value else "❌ MISSING")


debug_env_vars()


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise EnvironmentError(f"Missing environment variable: {name}")
    return value


def check_required_vars() -> None:
    required_vars = [
        "NOTION_API_KEY",
        "NOTION_DATABASE_ID",
        "REDDIT_CLIENT_ID",
        "REDDIT_CLIENT_SECRET",
        "REDDIT_USERNAME",
        "REDDIT_PASSWORD",
    ]
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        raise EnvironmentError(
            "\u274c Missing environment variables: " + ", ".join(missing)
        )


def create_clients() -> tuple[Client, praw.Reddit]:
    """Initialise Notion and Reddit clients from environment variables."""

    notion = Client(auth=_require_env("NOTION_API_KEY"))
    reddit = praw.Reddit(
        client_id=_require_env("REDDIT_CLIENT_ID"),
        client_secret=_require_env("REDDIT_CLIENT_SECRET"),
        username=_require_env("REDDIT_USERNAME"),
        password=_require_env("REDDIT_PASSWORD"),
        user_agent="blog-to-reddit-script",
    )
    return notion, reddit


def post_latest_blog(
    notion: Client, reddit: praw.Reddit, subreddit_name: str, database_id: str
) -> None:
    """Fetch the latest published blog post from Notion and post it to Reddit.

    After successfully posting, the entry is marked as ``Posted`` in Notion.
    """

    try:
        response = notion.databases.query(
            database_id=database_id,
            filter={"property": "Status", "select": {"equals": "Published"}},
            sorts=[{"timestamp": "created_time", "direction": "descending"}],
        )
    except Exception as exc:  # catching general errors as Notion API might raise various exceptions
        logging.error("Error querying Notion: %s", exc)
        return

    pages = response.get("results", [])
    if not pages:
        logging.info("No published posts found.")
        return

    page = pages[0]
    page_id = page["id"]
    title = "".join(t["plain_text"] for t in page["properties"]["Name"]["title"])
    content = "".join(
        t["plain_text"] for t in page["properties"]["Content"]["rich_text"]
    )

    try:
        reddit.subreddit(subreddit_name).submit(title=title, selftext=content)
        logging.info("✅ Posted: %s", title)
    except Exception as exc:
        logging.error("Error posting to Reddit: %s", exc)
        return

    # Mark the page as posted in Notion
    try:
        notion.pages.update(
            page_id=page_id,
            properties={"Status": {"select": {"name": "Posted"}}},
        )
    except Exception as exc:  # Notion might fail to update
        logging.error("Error updating Notion status: %s", exc)


def main() -> None:
    try:
        check_required_vars()
        notion, reddit = create_clients()
    except EnvironmentError as exc:
        logging.error(exc)
        return

    database_id = os.getenv("NOTION_DATABASE_ID")
    subreddit_name = os.getenv("REDDIT_SUBREDDIT", "test")
    post_latest_blog(notion, reddit, subreddit_name, database_id)


if __name__ == "__main__":
    main()
