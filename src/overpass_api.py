import requests
import json
from . import coordinates as c

def query(bbox:c.BoundingBox):
    overpass_url = "http://overpass-api.de/api/interpreter"
    query = f"""
    [out:json][timeout:25];
    (
        way["building:part"]({bbox.bottomLeft.latitude},{bbox.bottomLeft.longitude},{bbox.topRight.latitude},{bbox.topRight.longitude});
    );
    out body;
    >;
    out geom qt;
    """
    response = requests.post(overpass_url, data=query)
    response.raise_for_status()
    return response.json()