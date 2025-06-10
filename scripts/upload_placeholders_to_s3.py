import os
import boto3
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.getenv('AWS_REGION')
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')

if not all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, S3_BUCKET_NAME]):
    raise RuntimeError('AWS credentials and S3_BUCKET_NAME must be set in .env')

s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION,
)

def upload_file(path: Path):
    key = f"placeholders/{path.name}"
    s3_client.upload_file(
        str(path), S3_BUCKET_NAME, key,
        ExtraArgs={'ACL': 'public-read', 'ContentType': 'video/mp4'}
    )
    url = f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{key}"
    print(f"Uploaded {path} -> {url}")
    return url


def main():
    video_dir = Path('placeholders')
    if not video_dir.exists():
        raise SystemExit('placeholders/ directory not found. Add your mp4 files there.')

    for mp4 in video_dir.glob('*.mp4'):
        upload_file(mp4)

if __name__ == '__main__':
    main()
