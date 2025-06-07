import os
import argparse
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account

SCOPES = ["https://www.googleapis.com/auth/drive.file"]


def upload_gpt_library(folder: str, folder_id: str, creds_path: str) -> None:
    """Upload all files from *folder* into the given Google Drive folder."""
    creds = service_account.Credentials.from_service_account_file(
        creds_path, scopes=SCOPES
    )
    service = build("drive", "v3", credentials=creds)

    def upload_file(filepath: str) -> None:
        file_metadata = {"name": os.path.basename(filepath), "parents": [folder_id]}
        media = MediaFileUpload(filepath, resumable=True)
        service.files().create(
            body=file_metadata, media_body=media, fields="id"
        ).execute()

    for root, _, files in os.walk(folder):
        for file in files:
            full_path = os.path.join(root, file)
            upload_file(full_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload GPT library to Google Drive")
    parser.add_argument(
        "--folder",
        default=os.getenv("GPT_LIBRARY_PATH", ""),
        help="Path to local GPT library",
    )
    parser.add_argument(
        "--folder_id",
        default=os.getenv("DRIVE_FOLDER_ID"),
        help="Google Drive destination folder ID",
    )
    parser.add_argument(
        "--creds",
        default=os.getenv("SERVICE_ACCOUNT_FILE", "credentials.json"),
        help="Service account credentials JSON",
    )

    args = parser.parse_args()
    if not args.folder or not args.folder_id:
        parser.error(
            "--folder and --folder_id are required (set env vars or pass flags)"
        )

    upload_gpt_library(args.folder, args.folder_id, args.creds)
