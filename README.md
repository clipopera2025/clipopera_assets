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

## ClipOpera Neon Generator

`clipopera_ad_generator.html` is a browser based "Neon" generator. It lets you upload an image and optional audio track, add overlay text, pick a fit mode, and instantly preview the result. You can export the composition as an animated GIF or an MP4 video. Buttons demonstrate how a generated clip could be sent to Notion, Discord, or Google Drive (you must provide your own API credentials to enable those uploads).
