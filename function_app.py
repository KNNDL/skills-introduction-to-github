# function_app.py
import azure.functions as func
from upload_image import main as upload_image_main
from detect_image import main as detect_image_main

app = func.FunctionApp()

@app.function_name(name="upload_image")
@app.route(route="upload", auth_level=func.AuthLevel.ANONYMOUS)
def upload_image(req: func.HttpRequest) -> func.HttpResponse:
    return upload_image_main(req)

@app.function_name(name="detect_image")
@app.blob_trigger(arg_name="blob", path="images/{name}", connection="AzureWebJobsStorage")
def detect_image(blob: func.InputStream):
    detect_image_main(blob)
