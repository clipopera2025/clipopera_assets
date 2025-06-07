# clipopera_assets

## Sending Chat Logs to Notion

You can export conversations automatically with a browser extension or upload Markdown files using the helper script.

### Automated Export with Chrome Extension

Install the **ChatGPT to Notion - Batch Export** Chrome extension. It lets you sync multiple ChatGPT conversations to your Notion workspace in one click.

### Upload with `send_to_notion.py`

Install the required dependencies first:

```bash
pip install -r requirements.txt
```

Then provide a Notion integration token and page ID via environment variables:

```bash
export NOTION_TOKEN="<your integration token>"
export NOTION_PAGE_ID="<page id>"
python send_to_notion.py Fashion_Alchemist_Chat_2025-06-07.md "Fashion Alchemist Chat"
```

The script creates a new child page containing the chat log.
