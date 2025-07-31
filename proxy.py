from fastapi import FastAPI
from fastapi.responses import Response
import requests

app = FastAPI()

@app.get("/")
def fetch_track(track: str) -> Response:
    xml = requests.get(f"https://cloud.execvebin.sh/index.php/s/{track}/download").content
    return Response(content=xml, media_type="application/xml")
