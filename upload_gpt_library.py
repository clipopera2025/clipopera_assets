import argparse
import json
import mimetypes
import os
from typing import Dict, Tuple

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account

SCOPES = ["https://www.googleapis.com/auth/drive.file"]

SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE", "credentials.json")

# Root folder in Drive to upload into
ROOT_FOLDER_ID = os.getenv("DRIVE_ROOT_FOLDER_ID") or os.getenv("DRIVE_FOLDER_ID")


def build_service(creds_path: str):
    creds = service_account.Credentials.from_service_account_file(
        creds_path, scopes=SCOPES
    )
    return build("drive", "v3", credentials=creds)


def get_or_create_folder_path(
    service, folder_path: str, parent_id: str, cache: Dict[Tuple[str, str], str]
) -> str:
    """Return Drive folder ID, creating intermediate folders as needed."""

    segments = [s for s in folder_path.split(os.sep) if s]
    current_parent = parent_id

    for segment in segments:
        key = (segment, current_parent)
        if key in cache:
            current_parent = cache[key]
            continue

        query = (
            f"'{current_parent}' in parents and "
            f"name = '{segment}' and "
            "mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        )
        response = (
            service.files()
            .list(q=query, spaces="drive", fields="files(id, name)")
            .execute()
        )
        files = response.get("files", [])

        if files:
            folder_id = files[0]["id"]
        else:
            metadata = {
                "name": segment,
                "mimeType": "application/vnd.google-apps.folder",
                "parents": [current_parent],
            }
            folder = service.files().create(body=metadata, fields="id").execute()
            folder_id = folder["id"]

        cache[key] = folder_id
        current_parent = folder_id

    return current_parent


def upload_file(service, local_path: str, parent_id: str, dry_run: bool):
    mime_type, _ = mimetypes.guess_type(local_path)
    metadata = {"name": os.path.basename(local_path), "parents": [parent_id]}
    media = MediaFileUpload(local_path, mimetype=mime_type, resumable=True)

    if dry_run:
        print(f"[DRY-RUN] Would upload {local_path}")
        return {"file": local_path, "drive_id": "DRY-RUN"}

    uploaded = (
        service.files().create(body=metadata, media_body=media, fields="id").execute()
    )
    print(f"Uploaded {local_path} to Drive (ID: {uploaded['id']})")
    return {"file": local_path, "drive_id": uploaded["id"]}


def upload_gpt_library(
    folder: str, folder_id: str, creds_path: str, dry_run: bool
) -> None:
    service = build_service(creds_path)
    cache: Dict[Tuple[str, str], str] = {}
    manifest = []

    for root, _, files in os.walk(folder):
        for file in files:
            local_path = os.path.join(root, file)
            rel_path = os.path.relpath(local_path, folder)
            drive_parent = get_or_create_folder_path(
                service, os.path.dirname(rel_path), folder_id, cache
            )
            result = upload_file(service, local_path, drive_parent, dry_run)
            result["file"] = rel_path
            manifest.append(result)

    with open("upload_manifest.json", "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)
    print("Manifest saved to upload_manifest.json")


def main() -> None:
    parser = argparse.ArgumentParser(description="Upload GPT library to Google Drive")
    parser.add_argument("local_folder", help="Path to local library")
    parser.add_argument(
        "--dry-run", action="store_true", help="Simulate without uploading"
    )
    parser.add_argument(
        "--folder_id",
        default=ROOT_FOLDER_ID,
        help="Destination folder ID (DRIVE_ROOT_FOLDER_ID)",
    )
    parser.add_argument(
        "--creds",
        default=SERVICE_ACCOUNT_FILE,
        help="Service account credentials JSON",
    )

    args = parser.parse_args()

    if not args.folder_id:
        parser.error("--folder_id or DRIVE_ROOT_FOLDER_ID is required")

    upload_gpt_library(args.local_folder, args.folder_id, args.creds, args.dry_run)


if __name__ == "__main__":
    main()
