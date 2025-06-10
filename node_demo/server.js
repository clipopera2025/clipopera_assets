require('dotenv').config();
const express = require('express');
const multer = require('multer');
const AWS = require('aws-sdk');
const axios = require('axios');
const path = require('path');
const fs = require('fs');

const app = express();
const upload = multer({ dest: 'uploads/' });

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

app.listen(3000, () => {
  console.log('Server running on http://localhost:3000');
});
