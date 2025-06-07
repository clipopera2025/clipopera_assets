# Fashion Alchemist Uploader

This folder contains tools for uploading chat logs to Notion.

```
\_ logs/               # Place your `.md` chat logs here
\_ notion_batch_uploader.py
\_ requirements.txt
```

### Automated Export with Chrome Extension

Install the **ChatGPT to Notion - Batch Export** Chrome extension to quickly sync multiple conversations to your workspace.

### Upload a Single Markdown File

Install dependencies and run the helper script:

```bash
pip install -r requirements.txt
export NOTION_TOKEN="<your integration token>"
export NOTION_PAGE_ID="<page id>"
python ../send_to_notion.py logs/Fashion_Alchemist_Chat_2025-06-07.md "Fashion Alchemist Chat"
```

The script creates a new child page containing the chat log.

### Batch Upload to a Database

1. In Notion create a database with these properties:
   | Property | Type | Description |
   | --- | --- | --- |
   | Name | Title | Automatically filled with the Markdown filename. |
   | Tags | Multi-select | Populated from **Tags:** in the `.md` file. |
   | Topics | Multi-select | Populated from **Topics:** in the `.md` file. |
   | Quote | Text | Extracted from the `### Quote` block. |
2. Copy the database link and extract the 32-character ID.
3. Set environment variables and run the batch uploader:

```bash
export NOTION_TOKEN="<your integration token>"
export NOTION_PAGE_ID="<database id>"
python notion_batch_uploader.py
```

The script scans Markdown files in `logs/` and uploads each one as a page.
