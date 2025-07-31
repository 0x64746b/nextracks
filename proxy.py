from fastapi import FastAPI
from fastapi.responses import HTMLResponse, Response
import requests

app = FastAPI()

@app.get("/index.html")
def serve() -> HTMLResponse:
    with open("index.html") as f:
        html = f.read()
        return HTMLResponse(content=html, status_code=200)

@app.get("/")
def fetch_track(track: str) -> Response:
    xml = requests.get(f"https://cloud.execvebin.sh/index.php/s/{track}/download").content
    return Response(content=xml, media_type="application/xml")
