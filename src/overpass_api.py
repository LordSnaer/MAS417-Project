import requests
import json
from . import coordinates as c

def query(bbox:c.BoundingBox):
    overpass_url = "http://overpass-api.de/api/interpreter"
    bboxStr = f"{bbox.bottomLeft.latitude},{bbox.bottomLeft.longitude},{bbox.topRight.latitude},{bbox.topRight.longitude}"
    query = f"""
    [out:json][timeout:25];
    (
        way["building"]({bboxStr});
        way["building:part"]({bboxStr});
    );
    (._;>;);
    out body;
    """
    response = requests.post(overpass_url, data=query)
    response.raise_for_status()
    return response.json()