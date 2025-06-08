# ClipOpera Assets

This repository stores web and 3D assets for the **ClipOpera** project.

The interactive retro advertisement page now lives in `docs/index.html` and is automatically published with **GitHub Pages** via the included workflow. Open that page in a browser to experiment with text editing, theme switching, voice playback, and PNG export.

Large `.glb` model files are located under `assets/models`. New binary assets are tracked with **Git LFS** to keep the repository lean.

To clone with LFS support:

```bash
git lfs install
git clone <repo-url>
```

After pushing to the `main` branch, the site will deploy automatically.
