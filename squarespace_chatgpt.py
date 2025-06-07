import csv
import os
import argparse
from dotenv import load_dotenv
import openai
import requests

load_dotenv()

SQUARESPACE_API_KEY = os.getenv("SQUARESPACE_API_KEY")
SQUARESPACE_SITE_ID = os.getenv("SQUARESPACE_SITE_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

BASE_URL = "https://api.squarespace.com/1.0"


def generate_description(name: str) -> str:
    """Generate a short marketing description using ChatGPT."""
    prompt = "Write a concise, engaging product description for the item: " f"{name}."
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message["content"].strip()


def update_product_description(product_id: str, description: str) -> None:
    """Update Squarespace product description."""
    if not (SQUARESPACE_API_KEY and SQUARESPACE_SITE_ID):
        raise RuntimeError("SQUARESPACE_API_KEY and SQUARESPACE_SITE_ID must be set")

    url = f"{BASE_URL}/commerce/products/{product_id}"
    headers = {
        "Authorization": f"Bearer {SQUARESPACE_API_KEY}",
        "Content-Type": "application/json",
        "User-Agent": "ClipOpera-Client",
    }
    payload = {"fullDescription": description}
    resp = requests.patch(url, json=payload, headers=headers)
    if resp.ok:
        print(f"Updated {product_id}")
    else:
        print(f"Failed to update {product_id}: {resp.text}")


def process_csv(csv_path: str) -> None:
    with open(csv_path, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            product_id = row.get("id") or row.get("ID")
            name = row.get("name") or row.get("Name")
            if not product_id or not name:
                print("Skipping row with missing ID or name")
                continue
            description = generate_description(name)
            update_product_description(product_id, description)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate product descriptions with ChatGPT and update Squarespace",
    )
    parser.add_argument("csv_file", help="CSV file with Squarespace product data")
    args = parser.parse_args()
    process_csv(args.csv_file)
