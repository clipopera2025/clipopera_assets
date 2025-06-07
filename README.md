# clipopera_assets

## Sending Chat Logs to Notion

Use the `send_to_notion.py` script to upload a Markdown file to a Notion page. You must provide a Notion integration token and page ID via environment variables:

```bash
export NOTION_TOKEN="<your integration token>"
export NOTION_PAGE_ID="<page id>"
python send_to_notion.py Fashion_Alchemist_Chat_2025-06-07.md "Fashion Alchemist Chat"
```

The script creates a new child page containing the chat log.
