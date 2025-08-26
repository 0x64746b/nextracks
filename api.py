from io import BytesIO
import os
from tempfile import NamedTemporaryFile
from typing import Annotated

import contextily as cx
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse, HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from gpx_converter import Converter
import matplotlib
import pandas as pd
from rasterio import CRS
import requests

# Use non-interactive backend for plotting
matplotlib.use('agg')

app = FastAPI()

templates = Jinja2Templates(directory="templates")

@app.get("/")
def serve(request: Request) -> HTMLResponse:
    if original_proto := request.headers.get('x-forwarded-proto'):
        request.scope['scheme'] = original_proto  # enable generation of `HTTPS` URLs

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"og_image_url": _construct_preview_image_url(request)},
    )

@app.get("/preview-image")
def generate_preview_image(track: Annotated[list[str], Query()]) -> Response:
    gpx = pd.DataFrame()

    for id in track:
        try:
            response = requests.get(f"https://{os.environ['NEXTRACKS_NC_DOMAIN']}/index.php/s/{id}/download")
            response.raise_for_status()
        except requests.HTTPError as error:
            print(f"ERROR: Failed to fetch track for preview image: {error}")
        else:
            gpx = pd.concat([gpx, _parse_gpx(response.content)])

    if gpx.empty:
        raise HTTPException(status_code=400, detail="No valid tracks found")

    image: bytes = _plot_gpx(gpx)

    return Response(content=image, media_type="image/png")

@app.get("/track/{id}")
def fetch_track(id: str) -> Response:
    response = requests.get(f"https://{os.environ['NEXTRACKS_NC_DOMAIN']}/index.php/s/{id}/download")
    response.raise_for_status()
    return Response(content=response.content, media_type="application/xml")

def _construct_preview_image_url(request: Request) -> str:
    track_params = "&".join([f"track={tid}" for tid in request.query_params.getlist("track")])
    return f"{ request.url_for('generate_preview_image') }?{ track_params }"

def _parse_gpx(xml: bytes) -> pd.DataFrame:
    with NamedTemporaryFile(delete_on_close=False, suffix='.gpx') as tmp_file:
         tmp_file.write(xml)
         tmp_file.close()
         return Converter(tmp_file.name).gpx_to_dataframe()

def _plot_gpx(data: pd.DataFrame) -> bytes:
    ax = data.plot(x='longitude', y='latitude')
    ax.set_axis_off()
    ax.get_legend().remove()
    cx.add_basemap(ax, source=cx.providers.OpenStreetMap.DE, crs=CRS.from_epsg(4326))

    image_file = BytesIO()
    matplotlib.pyplot.savefig(image_file, format='png', bbox_inches='tight', pad_inches=0)
    image_file.seek(0)

    return image_file.read()
