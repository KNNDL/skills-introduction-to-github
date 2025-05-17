import logging
import azure.functions as func
from azure.storage.blob import BlobServiceClient
import os
from azure.ai.contentsafety import ContentSafetyClient
from azure.ai.contentsafety.models import AnalyzeImageOptions, ImageData
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
import imghdr

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
        logging.error(f"Content Safety analysis failed: {e}")
        return [f"Error: {e}"]

def main(blob: func.InputStream):
    logging.info(f"Blob trigger function processed blob \n"
                 f"Name: {blob.name}\n"
                 f"Blob Size: {blob.length} bytes")

    image_bytes = blob.read()

    # Validate image
    if not imghdr.what(None, h=image_bytes):
        logging.error("Uploaded blob is not a valid image.")
        return

    # Analyze image content
    analysis_results = analyze_image(image_bytes)
    logging.info(f"Content Safety analysis results:\n" + "\n".join(analysis_results))
