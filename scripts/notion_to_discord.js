// Utility script to post new Notion entries to Discord.
const { Client } = require('@notionhq/client');
const { google } = require('googleapis');
const fs = require('fs');
require('dotenv').config();

const NOTION_TOKEN = process.env.NOTION_TOKEN;
const NOTION_DATABASE_ID = process.env.NOTION_DATABASE_ID;
const DISCORD_WEBHOOK_URL = process.env.DISCORD_WEBHOOK_URL;
const GDRIVE_FOLDER_ID = process.env.GDRIVE_FOLDER_ID;

if (!NOTION_TOKEN || !NOTION_DATABASE_ID || !DISCORD_WEBHOOK_URL) {
  console.error('Missing required environment variables.');
  process.exit(1);
}

const notion = new Client({ auth: NOTION_TOKEN });

async function fetchNotionEntries() {
  const response = await notion.databases.query({
    database_id: NOTION_DATABASE_ID,
    filter: {
      property: 'Status',
      rich_text: {
        equals: 'New'
      }
    },
  });
  return response.results;
}

async function sendToDiscord(entry, driveUrl) {
  const payload = {
    content: entry.properties.Name?.title?.[0]?.plain_text || 'New Entry',
    embeds: [
      {
        title: entry.properties.Name?.title?.[0]?.plain_text || 'New Entry',
        description: entry.properties.Description?.rich_text?.[0]?.plain_text || '',
        url: driveUrl || null
      }
    ]
  };

  await fetch(DISCORD_WEBHOOK_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
}

async function uploadToDrive(filepath, filename) {
  if (!GDRIVE_FOLDER_ID) return null;
  const auth = await google.auth.getClient({ scopes: ['https://www.googleapis.com/auth/drive.file'] });
  const drive = google.drive({ version: 'v3', auth });

  const res = await drive.files.create({
    requestBody: {
      name: filename,
      parents: [GDRIVE_FOLDER_ID]
    },
    media: {
      body: fs.createReadStream(filepath)
    },
    fields: 'id, webViewLink'
  });

  return res.data.webViewLink;
}

async function run() {
  const entries = await fetchNotionEntries();
  for (const entry of entries) {
    let driveUrl = null;
    const fileProp = entry.properties.File;
    if (fileProp && fileProp.files && fileProp.files.length > 0) {
      const file = fileProp.files[0];
      const url = file.file ? file.file.url : file.external?.url;
      if (url) {
        const tempPath = `/tmp/${Date.now()}-${file.name || 'file'}`;
        const res = await fetch(url);
        const buffer = await res.arrayBuffer();
        fs.writeFileSync(tempPath, Buffer.from(buffer));
        try {
          driveUrl = await uploadToDrive(tempPath, file.name || 'upload');
        } finally {
          fs.unlinkSync(tempPath);
        }
      }
    }
    await sendToDiscord(entry, driveUrl);
  }
}

run().catch(err => {
  console.error(err);
  process.exit(1);
});
