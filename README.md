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

### Batch upload to a Notion database

1. In Notion create a database (table view recommended) with these properties:

   | Property | Type | Description |
   | --- | --- | --- |
   | Name | Title | Automatically filled with the Markdown filename. |
   | Tags | Multi-select | Populated from **Tags:** in the `.md` file. |
   | Topics | Multi-select | Populated from **Topics:** in the `.md` file. |
   | Quote | Text | Extracted from the `### Quote` block. |

2. Copy the database link and extract the 32‑character ID.

Set environment variables and run the batch uploader:

```bash
export NOTION_TOKEN="<your integration token>"
export NOTION_PAGE_ID="<database id>"
python notion_batch_uploader.py
```

The script scans Markdown files in the current directory and uploads each one as
a new page in the database using the properties above.
