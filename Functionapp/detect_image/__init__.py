import logging
import mimetypes
import os
import requests
from azure.storage.blob import BlobServiceClient
import azure.functions as func

def is_image(content_type: str, extension: str) -> bool:
    image_exts = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"}
    return content_type.startswith("image/") or extension.lower() in image_exts

def analyze_with_content_safety(image_bytes: bytes, api_key: str, endpoint: str) -> dict:
    url = f"{endpoint}/contentsafety/image:analyze?api-version=2023-10-01"
    headers = {
        "Ocp-Apim-Subscription-Key": api_key,
        "Content-Type": "application/octet-stream"
    }
    response = requests.post(url, headers=headers, data=image_bytes)
    response.raise_for_status()
    return response.json()

def main(blob: func.InputStream):
    logging.info(f"Processing blob: {blob.name} (Size: {blob.length} bytes)")

    file_name = blob.name.split('/')[-1]
    extension = os.path.splitext(file_name)[1]
    content_type, _ = mimetypes.guess_type(file_name)
    content_type = content_type or ""

    if not is_image(content_type, extension):
        logging.info(f"'{file_name}' is not an image.")
        return

    logging.info(f"'{file_name}' is identified as an image. Sending to Content Safety...")

    api_key = os.environ.get("CONTENT_SAFETY_KEY")
    endpoint = os.environ.get("CONTENT_SAFETY_ENDPOINT")

    if not api_key or not endpoint:
        logging.error("Missing CONTENT_SAFETY_KEY or CONTENT_SAFETY_ENDPOINT.")
        return

    try:
        result = analyze_with_content_safety(blob.read(), api_key, endpoint)
        logging.info(f"Content Safety result for '{file_name}': {result}")
    except Exception as e:
        logging.error(f"Failed to analyze '{file_name}' with Content Safety: {e}")
