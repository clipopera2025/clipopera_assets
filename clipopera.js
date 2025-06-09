const canvas = document.createElement('canvas');
canvas.id = 'previewCanvas';
canvas.width = 300;
canvas.height = 480;
document.body.insertBefore(canvas, document.querySelector('script')); // insert before script tags

const controls = document.createElement('div');
controls.id = 'controls';
controls.innerHTML = `
  <select id="fitMode">
    <option value="contain">Contain</option>
    <option value="cover">Cover</option>
  </select>
  <button id="exportGIF">\uD83D\uDDBC\uFE0F Export GIF</button>
  <button id="exportMP4">\uD83C\uDFA5 Export MP4</button>
  <input type="file" id="upload" accept="image/*,video/*" />
`;
document.body.insertBefore(controls, document.querySelector('script'));

const ctx = canvas.getContext('2d');
const upload = document.getElementById('upload');
let mediaElement;

function fitMedia(media) {
  const mode = document.getElementById('fitMode').value;
  const { width, height } = media.videoWidth ? { width: media.videoWidth, height: media.videoHeight } : media;
  const srcAspect = width / height;
  const canvasAspect = canvas.width / canvas.height;
  let drawW, drawH, x, y;
  if (mode === 'cover' ? srcAspect < canvasAspect : srcAspect > canvasAspect) {
    drawH = canvas.height;
    drawW = drawH * srcAspect;
  } else {
    drawW = canvas.width;
    drawH = drawW / srcAspect;
  }
  x = (canvas.width - drawW) / 2;
  y = (canvas.height - drawH) / 2;
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.drawImage(media, x, y, drawW, drawH);
}

upload.addEventListener('change', e => {
  const file = e.target.files[0];
  if (!file) return;
  const url = URL.createObjectURL(file);
  const isVideo = file.type.startsWith('video');
  mediaElement = document.createElement(isVideo ? 'video' : 'img');
  mediaElement.crossOrigin = 'anonymous';
  mediaElement.src = url;
  if (isVideo) {
    mediaElement.onloadeddata = () => {
      mediaElement.currentTime = 0;
      mediaElement.play();
      setInterval(() => fitMedia(mediaElement), 1000);
    };
  } else {
    mediaElement.onload = () => fitMedia(mediaElement);
  }
});

function exportGIF() {
  if (!mediaElement) return;
  const gif = new GIF({ workers: 2, quality: 10, width: canvas.width, height: canvas.height });
  let frameCount = 10;
  for (let i = 0; i < frameCount; i++) {
    fitMedia(mediaElement);
    gif.addFrame(ctx, { copy: true, delay: 100 });
  }
  gif.on('finished', blob => {
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'clipopera.gif';
    link.click();
  });
  gif.render();
}

async function exportMP4() {
  if (!mediaElement || !mediaElement.videoWidth) return;
  const { createFFmpeg, fetchFile } = FFmpeg;
  const ffmpeg = createFFmpeg({ log: true });
  await ffmpeg.load();

  const tempCanvas = document.createElement('canvas');
  const tempCtx = tempCanvas.getContext('2d');
  tempCanvas.width = canvas.width;
  tempCanvas.height = canvas.height;
  let frameNames = [];

  for (let i = 0; i < 10; i++) {
    fitMedia(mediaElement);
    tempCtx.drawImage(canvas, 0, 0);
    const blob = await new Promise(resolve => tempCanvas.toBlob(resolve, 'image/png'));
    const name = `frame${i}.png`;
    ffmpeg.FS('writeFile', name, await fetchFile(blob));
    frameNames.push(name);
  }

  await ffmpeg.run('-framerate', '1', '-i', 'frame%d.png', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', 'output.mp4');
  const data = ffmpeg.FS('readFile', 'output.mp4');
  const videoBlob = new Blob([data.buffer], { type: 'video/mp4' });
  const url = URL.createObjectURL(videoBlob);
  const link = document.createElement('a');
  link.href = url;
  link.download = 'clipopera.mp4';
  link.click();
}

document.getElementById('exportGIF').addEventListener('click', exportGIF);
document.getElementById('exportMP4').addEventListener('click', exportMP4);
