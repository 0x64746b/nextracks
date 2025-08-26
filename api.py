from io import BytesIO
import os
import socket
from tempfile import NamedTemporaryFile

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from gpx_converter import Converter
import matplotlib
from pandas import DataFrame
import requests

# force use of IPv6
requests.packages.urllib3.util.connection.allowed_gai_family = lambda: socket.AF_INET6

# Use non-interactive backend for plotting
matplotlib.use('agg')

app = FastAPI()

templates = Jinja2Templates(directory="templates")

@app.get("/")
def serve(request: Request) -> HTMLResponse:
    request.scope['scheme'] = 'https' # FIXME: force generation of `HTTPS` URLs
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/preview-image/{id}")
def generate_preview_image(id: str) -> Response:
    response = requests.get(f"https://{os.environ['NEXTRACKS_NC_DOMAIN']}/index.php/s/{id}/download")
    response.raise_for_status()
    gpx: DataFrame = _parse_gpx(response.content)
    image: bytes = _plot_gpx(gpx)

    return Response(content=image, media_type="image/png")

@app.get("/track/{id}")
def fetch_track(id: str) -> Response:
    response = requests.get(f"https://{os.environ['NEXTRACKS_NC_DOMAIN']}/index.php/s/{id}/download")
    response.raise_for_status()
    return Response(content=response.content, media_type="application/xml")

def _parse_gpx(xml: bytes) -> DataFrame:
    with NamedTemporaryFile(delete_on_close=False, suffix='.gpx') as tmp_file:
         tmp_file.write(xml)
         tmp_file.close()
         return Converter(tmp_file.name).gpx_to_dataframe()

def _plot_gpx(data: DataFrame) -> bytes:
    data.plot(x='longitude', y='latitude')

    image_file = BytesIO()
    matplotlib.pyplot.savefig(image_file, format='png')
    image_file.seek(0)

    return image_file.read()
