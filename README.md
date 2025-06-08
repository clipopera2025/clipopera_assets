# clipopera_assets

This repository contains assets for the ClipOpera project, including 3D model files and planning documents.

## Google Apps Script

You can use the provided `SoraForm.gs` script to create a simple Google Form that triggers OpenAI's Sora video generation API.

### Steps
1. Visit [Google Apps Script](https://script.google.com/) and create a new project.
2. Delete any code in `Code.gs` and replace it with the contents of `SoraForm.gs`.
3. Update `YOUR_OPENAI_API_KEY` with your OpenAI API key.
4. Save the project and run the `createSoraForm` function to generate the form.

When the form is submitted with "Generate Video?" set to "Yes," it will send a request to the OpenAI API to start video generation.


## Notion to Discord Automation

The `scripts/notion_to_discord.js` script fetches pages from a Notion database and posts formatted messages to a Discord channel. Optionally, media links can be uploaded to Google Drive and the shared URL is included in the Discord message.

### Set Up the Environment
Create a `.env` file in the project root containing:

```
NOTION_TOKEN=secret_yourNotionIntegrationToken
NOTION_DATABASE_ID=yourNotionDatabaseID
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/yourWebhookID
GDRIVE_FOLDER_ID=yourGoogleDriveFolderID  # optional if uploading media
```

### Notion Integration
1. In Notion, go to **Settings & Members → Integrations → Develop your own integrations**.
2. Create a new internal integration and copy the token.
3. Share your target database with that integration.

### Discord Setup
1. Create a test channel in your Discord server.
2. Go to **Channel Settings → Integrations → Webhooks → Create Webhook**.
3. Copy the webhook URL and add it to `DISCORD_WEBHOOK_URL` in `.env`.

### Optional Google Drive Upload
1. Create a Google Cloud project and enable the Drive API.
2. Generate a service account key JSON and set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to point to it.
3. Set `GDRIVE_FOLDER_ID` in your `.env` to the ID of the folder where uploads should be stored.

### Install Dependencies and Run
```bash
npm install dotenv @notionhq/client node-fetch googleapis
node scripts/notion_to_discord.js
```

After running the script you should see console messages similar to:

```
✔️ Fetched Notion pages
✔️ Posted formatted content to Discord
✔️ Uploaded media to Drive (if set) and posted URL in Discord message
```

Check your Discord channel to view the results.
