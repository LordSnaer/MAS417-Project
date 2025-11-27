import requests
import json
from . import coordinates as c

def query(bbox:c.BoundingBox):
    overpass_url = "http://overpass-api.de/api/interpreter"
    bboxStr = f"{bbox.bottomLeft.latitude},{bbox.bottomLeft.longitude},{bbox.topRight.latitude},{bbox.topRight.longitude}"
    query = f"""
    [out:json][timeout:100];
    (
        way["building"]({bboxStr});
        way["building:part"]({bboxStr});
    );
    (._;>;);
    out body;
    """
    response = requests.post(overpass_url, data=query)
    response.raise_for_status()

    try:
        with open("output/overpass_response.json", "w") as f:
            json.dump(response.json(), indent=4, fp=f)
    except Exception as exception:
        print(f"Could not save Overpass response to file: {exception}")

    return response.json()