import requests
import json
import coordinates

def query(bbox:coordinates.BoundingBox):
    overpass_url = "http://overpass-api.de/api/interpreter"
    query = f"""
    [out:json][timeout:25];
    (
        way["building"]({bbox.bottomLeft.latitude},{bbox.bottomLeft.longitude},{bbox.topRight.latitude},{bbox.topRight.longitude});
    );
    out body;
    >;
    out skel qt;
    """
    response = requests.post(overpass_url, data=query)
    response.raise_for_status()
    return response.json()