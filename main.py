import os
from src import (
    ui,
    overpass_api,
    mesh
)

bbox = ui.boundingBoxDialog()

if not os.path.exists("output"):
    os.mkdir("output")

response = overpass_api.query(bbox)

scale = ui.scaleDialog()

mesh.meshGeneration(bbox, scale, response)