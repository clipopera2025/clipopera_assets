# clipopera_assets

This repository contains assets and scripts used for ClipOpera projects.

## Notion to Discord Script

`scripts/notion_to_discord.js` fetches new entries from a Notion database and posts them to a Discord channel. If configured, uploaded media is stored in a Google Drive folder and the share link is included in the Discord message.

### Setup

1. Install dependencies using npm:
   ```bash
   npm install
   ```
2. Create a `.env` file in the repository root with the following variables (this file is ignored by Git; ensure `.gitignore` contains `.env`):
   ```ini
   NOTION_TOKEN=<your_notional_integration_token>
   NOTION_DATABASE_ID=<the database ID>
   DISCORD_WEBHOOK_URL=<your Discord webhook>
   # optional
   GDRIVE_FOLDER_ID=<your Google Drive folder ID>
   ```

### Running the Script

Execute the script with Node:

```bash
node scripts/notion_to_discord.js
```

The script will query the Notion database for entries where the `Status` property equals `New`, send the contents to Discord, and upload any attached file to Google Drive if a folder ID is provided.

## ClipOpera Ad Generator

`clipopera_ad_generator.html` is a simple in-browser tool for previewing images or videos and exporting a short GIF or MP4. Open the file in your browser, choose a fit mode, upload media, then export the result.

## Drive Chat Uploader

`drive_chat_uploader.py` uploads Markdown chat archives from a local `chats/` folder to Google Drive. Each file is summarized using OpenAI before upload.

### Setup

1. Install the Python dependencies:
   ```bash
   pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib openai
   ```
2. Place `credentials.json` next to the script and ensure a `chats/` directory exists with your `.md` archives.

### Running the Script

Export your OpenAI API key or provide it via `--openai-key`:

```bash
# Using environment variable
export OPENAI_API_KEY=<your-key>
python drive_chat_uploader.py --folder-id <GOOGLE_DRIVE_FOLDER_ID>

# Or passing the key directly
python drive_chat_uploader.py --folder-id <GOOGLE_DRIVE_FOLDER_ID> --openai-key <your-key>
```

On first run, a browser window will prompt for Google Drive authentication. Tokens are saved to `token.json` for subsequent runs.
