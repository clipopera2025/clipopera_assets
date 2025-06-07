# clipopera_assets

## Blog to Reddit Script

This repository includes a simple script for posting the most recent published Notion blog entry to Reddit.

### Setup

1. Ensure the directory structure is:

   ```
   blog-to-reddit/
   ├── post_blog.py
   ├── .env            # your secrets
   └── .env.example    # template
   ```

   The `.env` file must be in the same folder as `post_blog.py` and
   **named exactly `.env`** (no `.txt` extension).

2. Create that `.env` file with the following variables (see
   `blog-to-reddit/.env.example` for a template). Use **real values** and
   ensure there are no quotes, trailing spaces, or blank lines:

```
NOTION_API_KEY=<your notion integration secret>
NOTION_DATABASE_ID=<the id of your posts database>
REDDIT_CLIENT_ID=<reddit app client id>
REDDIT_CLIENT_SECRET=<reddit app client secret>
REDDIT_USERNAME=<reddit username>
REDDIT_PASSWORD=<reddit password>
REDDIT_SUBREDDIT=<subreddit to post to>
```

   After creating the file, run `python blog-to-reddit/post_blog.py` once
   to confirm it loads correctly. The script logs the value of
   `REDDIT_USERNAME` so you can verify the `.env` was read.

   If you want to double‑check in your own code, add this snippet right
   after calling `load_dotenv()`:

   ```python
   import logging

   logging.info("🔍 Checking environment variable loading:")
   logging.info("REDDIT_USERNAME: %s", os.getenv("REDDIT_USERNAME"))
   ```

3. Install the Python dependencies:

```bash
pip install praw python-dotenv notion-client
```

### Usage

Run the script from the repository root:

```bash
python blog-to-reddit/post_blog.py
```

If everything is configured correctly, the latest published post will appear on Reddit and the corresponding page in Notion will be marked as **Posted**.
The script prints which environment variables are set so you can verify your `.env` file was loaded.

### Automating

Use `cron` or a similar scheduler to call the script periodically if you want automated posting.
