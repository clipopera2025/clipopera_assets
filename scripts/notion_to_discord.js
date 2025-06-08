require('dotenv').config();
const { Client } = require('@notionhq/client');
const fetch = require('node-fetch');
const { google } = require('googleapis');
const path = require('path');

const notion = new Client({ auth: process.env.NOTION_TOKEN });

async function fetchPages() {
  const response = await notion.databases.query({
    database_id: process.env.NOTION_DATABASE_ID,
  });
  return response.results || [];
}

async function postToDiscord(content) {
  const webhook = process.env.DISCORD_WEBHOOK_URL;
  if (!webhook) throw new Error('DISCORD_WEBHOOK_URL not set');

  await fetch(webhook, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content }),
  });
}

function createDriveClient() {
  const auth = new google.auth.GoogleAuth({
    scopes: ['https://www.googleapis.com/auth/drive.file'],
  });
  return google.drive({ version: 'v3', auth });
}

async function uploadToDrive(url, filename) {
  const folderId = process.env.GDRIVE_FOLDER_ID;
  if (!folderId) return null;

  const drive = createDriveClient();
  const res = await fetch(url);
  const buffer = await res.buffer();

  const file = await drive.files.create({
    requestBody: { name: filename, parents: [folderId] },
    media: { mimeType: 'application/octet-stream', body: buffer },
    fields: 'id',
  });

  const fileId = file.data.id;
  await drive.permissions.create({
    fileId,
    requestBody: { role: 'reader', type: 'anyone' },
  });
  return `https://drive.google.com/uc?id=${fileId}`;
}

async function main() {
  const pages = await fetchPages();
  console.log('✔️ Fetched Notion pages');

  for (const page of pages) {
    const titleProp = page.properties.Name || page.properties.Title;
    const title = titleProp ? titleProp.title[0].plain_text : 'Untitled';
    let message = `**${title}**`;

    const mediaProp = page.properties.Media;
    if (mediaProp && mediaProp.url) {
      const url = mediaProp.url;
      const filename = path.basename(url);
      try {
        const driveLink = await uploadToDrive(url, filename);
        if (driveLink) message += `\n${driveLink}`;
      } catch (err) {
        console.error('Drive upload failed:', err.message);
      }
    }

    await postToDiscord(message);
    console.log('✔️ Posted formatted content to Discord');
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
