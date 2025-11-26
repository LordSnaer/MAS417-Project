from src import (
    ui,
    overpass_api,
    coordinates as c,
    mesh
)
import json
import os

#kristiansand domkirke
# coord1 = c.GlobalCoordinate(58.145923, 7.994083)
# coord2 = c.GlobalCoordinate(58.146344, 7.995170)

#nidarosdomen
coord1 = c.GlobalCoordinate(63.426619, 10.395700)
coord2 = c.GlobalCoordinate(63.427257, 10.398082)

#westminster
# coord1 = c.GlobalCoordinate(51.498034, -0.126185)
# coord2 = c.GlobalCoordinate(51.500831, -0.123484)

#bbox = c.BoundingBox(type="corners", Coord1=coord1, Coord2=coord2)

bbox = ui.boundingBoxDialog()

response = overpass_api.query(bbox)

if not os.path.exists("output"):
    os.mkdir("output")
try:
    with open("output/overpass_response.json", "w") as f:
        json.dump(response, indent=4, fp=f)
except Exception as e:
    print(f"Could not save Overpass response to file: {e}")

# scale = ui.scaleDialog()
scale = 10000
mesh.meshGeneration(bbox, scale, response)