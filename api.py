import os

from fastapi import FastAPI
from fastapi.responses import FileResponse, Response
import requests

app = FastAPI()

@app.get("/")
def serve() -> FileResponse:
    return FileResponse("index.html")

@app.get("/preview-image")
def generate_preview_image() -> FileResponse:
    return FileResponse("public/2024-09-08.jpg")

@app.get("/track/{id}")
def fetch_track(id: str) -> Response:
    xml = requests.get(f"https://{os.environ['NEXTRACKS_NC_DOMAIN']}/index.php/s/{id}/download").content
    return Response(content=xml, media_type="application/xml")
