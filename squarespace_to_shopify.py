import csv
import os
import argparse
import requests
from dotenv import load_dotenv

load_dotenv()

SHOPIFY_STORE = os.getenv("SHOPIFY_STORE")
SHOPIFY_API_KEY = os.getenv("SHOPIFY_API_KEY")
SHOPIFY_API_PASSWORD = os.getenv("SHOPIFY_API_PASSWORD")


def create_product(row: dict) -> dict:
    product = {
        "product": {
            "title": row.get("Name") or row.get("Item Name") or "Untitled",
            "body_html": row.get("Body") or row.get("Description", ""),
            "vendor": row.get("Vendor", ""),
            "variants": [
                {
                    "price": row.get("Variant Price") or row.get("Price", "0"),
                    "sku": row.get("Variant SKU") or row.get("SKU", ""),
                    "inventory_quantity": int(row.get("Quantity", "0")),
                }
            ],
        }
    }
    return product


def upload_products(csv_path: str) -> None:
    if not (SHOPIFY_STORE and SHOPIFY_API_KEY and SHOPIFY_API_PASSWORD):
        raise RuntimeError(
            "SHOPIFY_STORE, SHOPIFY_API_KEY, and SHOPIFY_API_PASSWORD must be set"
        )

    url = f"https://{SHOPIFY_API_KEY}:{SHOPIFY_API_PASSWORD}@{SHOPIFY_STORE}/admin/api/2023-07/products.json"

    with open(csv_path, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            product = create_product(row)
            resp = requests.post(url, json=product)
            if resp.ok:
                print(f"Uploaded product: {product['product']['title']}")
            else:
                print(f"Failed to upload {product['product']['title']}: {resp.text}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Migrate Squarespace product CSV to Shopify"
    )
    parser.add_argument("csv_file", help="Path to Squarespace exported CSV")
    args = parser.parse_args()
    upload_products(args.csv_file)
