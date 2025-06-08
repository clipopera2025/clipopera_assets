# ClipOpera Assets

This repository hosts the demo assets and HTML for **ClipOpera: The Gotham Ad Engine**.

## Setup

1. Install [Node.js](https://nodejs.org/) if you plan to run the HTML linter.
2. Clone the repository:
   ```bash
   git clone <repo-url>
   cd clipopera_assets
   ```
3. To lint the HTML, run:
   ```bash
   npx -y htmlhint 'docs/**/*.html'
   ```
   A GitHub Actions workflow will also run this automatically on pushes and pull requests.

## Usage

Open `docs/index.html` in a modern browser. The demo allows you to choose a template and see how ClipOpera loads media, voices, and simple fade transitions.

The `templates.json` file contains example template entries. You can extend this file with your own templates, providing media URLs and voice clips.

## Deployment

To publish the demo via GitHub Pages:

1. Enable GitHub Pages in your repository settings and select the `docs` folder as the source.
2. Visit `https://<username>.github.io/<repo-name>/index.html` after the site is built.

## Automation

The `.github/workflows/html-lint.yml` workflow lints HTML files under `docs/` on every push or pull request. If the linter detects errors, the workflow fails.

