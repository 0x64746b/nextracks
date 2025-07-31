from fastapi import FastAPI
from fastapi.responses import FileResponse, Response
import requests

app = FastAPI()

@app.get("/")
def serve() -> FileResponse:
    return FileResponse("index.html")

@app.get("/track/{id}")
def fetch_track(id: str) -> Response:
    xml = requests.get(f"https://cloud.execvebin.sh/index.php/s/{id}/download").content
    return Response(content=xml, media_type="application/xml")
