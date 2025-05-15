import logging
import azure.functions as func
from azure.storage.blob import BlobServiceClient
import os
import uuid
# Configure your connection
BLOB_CONNECTION_STRING = os.environ["AzureWebJobsStorage"]
CONTAINER_NAME = "dfcontainerwesteu"  # Use same container that triggers detect_image
def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Upload image function triggered.')
    try:
        # Check if file was uploaded
        file = req.files.get('file')
        if not file:
            return func.HttpResponse("No file uploaded", status_code=400)
        # Generate a unique file name (keep original extension)
        file_ext = os.path.splitext(file.filename)[-1]
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        # Upload to Blob Storage
        blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONNECTION_STRING)
        blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=unique_filename)
        blob_client.upload_blob(file.stream, overwrite=True)
        return func.HttpResponse(f"Image uploaded successfully: {unique_filename}", status_code=200)
    except Exception as e:
        logging.error(f"Error uploading image: {e}")
        return func.HttpResponse(f"Internal server error: {str(e)}", status_code=500)