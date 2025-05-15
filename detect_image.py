import logging
import azure.functions as func
from azure.storage.blob import BlobServiceClient
import os
from datetime import datetime
from azure.ai.contentsafety import ContentSafetyClient
from azure.ai.contentsafety.models import AnalyzeImageOptions, ImageData, ImageCategory
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
import imghdr

# Blob and Content Safety settings
STORAGE_CONNECTION_STRING = os.environ["AzureWebJobsStorage"]
CONTAINER_NAME = "dfcontainerwesteu"
CONTENT_SAFETY_KEY = "02RtNklbIs2BhAUIPv5aD6se5MDYhruHOCZFMAHXBf7qIkiTdxg7JQQJ99BEAC5RqLJXJ3w3AAAHACOGjft5"
CONTENT_SAFETY_ENDPOINT = "https://content-safety-dev-d.cognitiveservices.azure.com/"

def analyze_image(image_bytes: bytes):
    client = ContentSafetyClient(CONTENT_SAFETY_ENDPOINT, AzureKeyCredential(CONTENT_SAFETY_KEY))
    request = AnalyzeImageOptions(image=ImageData(content=image_bytes))
    try:
        response = client.analyze_image(request)
        results = []
        for category in response.categories_analysis:
            results.append(f"{category.category} severity: {category.severity}")
        return results
    except HttpResponseError as e:
        logging.error("Content Safety analysis failed.")
        return [f"Error: {e}"]

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Received image upload request.")
    try:
        file = req.files["file"]
        image_bytes = file.read()
    except Exception as e:
        return func.HttpResponse(f"Failed to read uploaded image: {e}", status_code=400)

    # Verify it's a valid image
    if not imghdr.what(None, h=image_bytes):
        return func.HttpResponse("Uploaded file is not a valid image.", status_code=400)

    # Save to Blob Storage
    try:
        blob_service_client = BlobServiceClient.from_connection_string(STORAGE_CONNECTION_STRING)
        blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=file.filename)
        blob_client.upload_blob(image_bytes, overwrite=True)
        logging.info(f"Uploaded image '{file.filename}' to blob storage.")
    except Exception as e:
        return func.HttpResponse(f"Failed to upload to Blob Storage: {e}", status_code=500)

    # Analyze with Content Safety
    analysis_results = analyze_image(image_bytes)
    return func.HttpResponse(f"Image uploaded and analyzed.\n\n" + "\n".join(analysis_results), status_code=200)
