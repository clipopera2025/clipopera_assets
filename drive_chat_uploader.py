import os
import argparse
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import openai

# If modifying these SCOPES, delete token.json
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def authenticate_drive():
    creds = None
    if os.path.exists('token.json'):
        with open('token.json', 'rb') as token_file:
            creds = pickle.load(token_file)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'wb') as token_file:
            pickle.dump(creds, token_file)
    return creds


def init_chatgpt(api_key=None):
    if api_key:
        openai.api_key = api_key
        return
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("Missing OPENAI_API_KEY environment variable")
    openai.api_key = api_key


def summarize_text(text: str) -> str:
    """Use ChatGPT to generate a brief summary for the provided text."""
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant for summarizing chat logs."},
            {"role": "user", "content": "Summarize the following chat content in 2-3 sentences:\n\n" + text}
        ],
        temperature=0.7,
        max_tokens=150
    )
    summary = response.choices[0].message.content.strip()
    return summary


def upload_files(service, folder_id, directory='chats'):
    for filename in os.listdir(directory):
        if filename.lower().endswith('.md'):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            try:
                summary = summarize_text(content)
                print(f"Summary for {filename}: {summary}")
            except Exception as e:
                print(f"ChatGPT summary failed for {filename}: {e}")

            file_metadata = {
                'name': filename,
                'parents': [folder_id]
            }
            media = MediaFileUpload(filepath, mimetype='text/markdown')
            file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            print(f"Uploaded {filename} (ID: {file.get('id')})")


def main():
    parser = argparse.ArgumentParser(description='Upload chat archives to Google Drive with optional ChatGPT processing')
    parser.add_argument('--folder-id', required=True, help='Drive folder ID to upload files into')
    parser.add_argument('--openai-key', help='OpenAI API key (optional if OPENAI_API_KEY env var is set)')
    args = parser.parse_args()

    creds = authenticate_drive()
    drive_service = build('drive', 'v3', credentials=creds)
    init_chatgpt(args.openai_key)

    upload_files(drive_service, args.folder_id)


if __name__ == '__main__':
    main()
