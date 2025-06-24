const express = require('express');
const path = require('path');

const app = express();
app.use(express.static(path.join(__dirname, 'views')));

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'views', 'avatar.html'));
});

const PORT = process.env.PORT || 4000;
app.listen(PORT, () => {
  console.log(`Avatar page available at http://localhost:${PORT}`);
});
