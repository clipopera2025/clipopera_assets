#!/bin/bash

# Install dependencies for ClipOpera Notion automation

set -e

echo "🔧 Installing ClipOpera Notion Automation Environment..."

# create and activate virtual environment
python3 -m venv env
source env/bin/activate

# upgrade pip
pip install --upgrade pip

# install required packages
pip install \
    Flask \
    notion-client \
    python-dotenv \
    google-api-python-client \
    google-auth-httplib2 \
    google-auth-oauthlib \
    openai \
    requests

echo "✅ Environment ready. You can now run create_notion_page.py"
