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

