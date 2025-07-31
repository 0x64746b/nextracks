from fastapi import FastAPI
from fastapi.responses import JSONResponse
import requests

app = FastAPI()

@app.get("/")
def fetch_track(track: str) -> JSONResponse:
    return requests.get(f"https://cloud.execvebin.sh/index.php/s/{track}/download").content