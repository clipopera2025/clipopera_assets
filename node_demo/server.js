require('dotenv').config();
const express = require('express');
const multer = require('multer');
const AWS = require('aws-sdk');
const axios = require('axios');
const path = require('path');
const fs = require('fs');

const app = express();
const upload = multer({ dest: 'uploads/' });

app.use(express.json());

app.use(express.static('views'));

AWS.config.update({
  accessKeyId: process.env.AWS_ACCESS_KEY_ID,
  secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
  region: process.env.AWS_REGION
});
const s3 = new AWS.S3();

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'views/index.html'));
});

app.post('/upload', upload.single('file'), (req, res) => {
  const file = req.file;
  const uploadParams = {
    Bucket: process.env.S3_BUCKET_NAME,
    Key: file.originalname,
    Body: fs.createReadStream(file.path)
  };
  s3.upload(uploadParams, (err, data) => {
    fs.unlinkSync(file.path);
    if (err) return res.status(500).send('Upload error');
    res.send(`File uploaded: <a href="${data.Location}">${data.Location}</a>`);
  });
});

app.get('/meta/login', (req, res) => {
  const loginUrl = `https://www.facebook.com/v18.0/dialog/oauth?client_id=${process.env.META_APP_ID}&redirect_uri=${process.env.META_REDIRECT_URI}&scope=ads_management`;
  res.redirect(loginUrl);
});

app.get('/meta/callback', async (req, res) => {
  const code = req.query.code;
  try {
    const response = await axios.get('https://graph.facebook.com/v18.0/oauth/access_token', {
      params: {
        client_id: process.env.META_APP_ID,
        client_secret: process.env.META_APP_SECRET,
        redirect_uri: process.env.META_REDIRECT_URI,
        code
      }
    });
    res.send(`<pre>${JSON.stringify(response.data, null, 2)}</pre>`);
  } catch (error) {
    res.status(500).send('Meta Auth Failed');
  }
});

async function translate(text, target) {
  if (!target || target === 'en') return text;
  try {
    const { data } = await axios.post(process.env.LIBRETRANSLATE_URL || 'https://libretranslate.de/translate', {
      q: text,
      source: 'en',
      target,
      format: 'text'
    });
    return data.translatedText || text;
  } catch (err) {
    console.error('Translation error', err.message);
    return text;
  }
}

app.post('/chat', async (req, res) => {
  const { prompt, lang } = req.body;
  if (!prompt) return res.status(400).json({ error: 'prompt required' });
  try {
    const { data } = await axios.post(process.env.GROK_API_URL || 'https://x.ai/api/grok', { prompt }, {
      headers: { Authorization: `Bearer ${process.env.GROK_API_KEY}` }
    });
    let text = data.text || data.response || data;
    text = await translate(text, lang);
    return res.json({ text });
  } catch (err) {
    try {
      const { data } = await axios.post('https://api.openai.com/v1/chat/completions', {
        model: 'gpt-3.5-turbo',
        messages: [{ role: 'user', content: prompt }]
      }, {
        headers: { Authorization: `Bearer ${process.env.OPENAI_API_KEY}` }
      });
      let text = data.choices[0].message.content;
      text = await translate(text, lang);
      return res.json({ text });
    } catch (fallbackErr) {
      console.error('LLM error', fallbackErr.message);
      return res.status(500).json({ error: 'LLM failure' });
    }
  }
});

app.listen(3000, () => {
  console.log('Server running on http://localhost:3000');
});
