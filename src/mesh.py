from unittest import case
from . import (
    coordinates as c,
    elements as e,
    roof as r
)
import math
import numpy as np
import stl
from shapely import Polygon, geometry
from shapely.ops import triangulate
import json
import trimesh

defaultMinHeight = 0.0
defaultHeight = 6.0
defaultFloorHeight = 3.0
defaultRoofShape = "flat"
defaultRoofHeight = 0.0
defaultBaseHeight = 5.0

def jsonParser(response:dict, bbox:c.BoundingBox) -> None:
    for element in response["elements"]:
        if element["type"] == "node":
            e.nodeDict[element["id"]] = c.globalToLocal(bbox.center, c.GlobalCoordinate(latitude=element["lat"], longitude=element["lon"]))
        elif element["type"] == "way":
            tags:dict = element["tags"]
            e.wayDict[element["id"]] = e.Way(
                nodes = element["nodes"],
                minHeight = float(tags.get("min_height", defaultMinHeight)),
                height = float(tags.get("height", defaultHeight)),
                roofShape = tags.get("roof:shape", defaultRoofShape),
                roofOrientation = tags.get("roof:orientation", ""),
                roofDirection = tags.get("roof:direction", ""),
                roofHeight = float(tags.get("roof:height", defaultRoofHeight)),
                type = ("building" if "building" in tags else ("part" if tags.get("building:part")=="yes" else ""))
            )
            if "levels" in tags and "height" not in tags:
                e.wayDict[element["id"]].height = int(tags["levels"]) * defaultFloorHeight

def meshGeneration(bbox:c.BoundingBox, scale:float, response:dict) -> None:
    jsonParser(response, bbox)
    xmin = - bbox.width / 2
    ymin = - bbox.height / 2
    xmax = bbox.width / 2
    ymax = bbox.height / 2
    basePolygon = geometry.Polygon().from_bounds(xmin, ymin, xmax, ymax)
    #create polygons for each way and remove those not fully within bounding box
    waysToRemove = []
    for id, way in e.wayDict.items():
        footprint = [e.nodeDict[nodeId].xy for nodeId in way.nodes]
        way.polygon = geometry.Polygon(footprint)
        if not basePolygon.contains(way.polygon):
            waysToRemove.append(id)
    for id in waysToRemove:
        e.wayDict.pop(id)
    waysToRemove.clear()
    #remove buildings that have building parts overlapping them]
    for partID in [id for id in list(e.wayDict.keys()) if e.wayDict[id].type == "part"]:
        for buildingID in [id for id in list(e.wayDict.keys()) if e.wayDict[id].type == "building"]:
            if buildingID not in waysToRemove and e.wayDict[buildingID].polygon.intersects(e.wayDict[partID].polygon):
                waysToRemove.append(buildingID)
    for id in waysToRemove:
            e.wayDict.pop(id)
    
    baseMesh = trimesh.creation.extrude_polygon(basePolygon, defaultBaseHeight)
    buildingMeshes = []
    for id, way in e.wayDict.items():
        wallHeight = way.height - way.minHeight - way.roofHeight
        offsetHeight = way.minHeight + defaultBaseHeight
        if wallHeight > 1e-3:
            buildingMeshes.append(trimesh.creation.extrude_polygon(way.polygon, wallHeight).apply_translation([0, 0, offsetHeight]))
        roof = r.roofMesh(way)
        if roof is not None:
            buildingMeshes.append(roof.apply_translation([0, 0, (wallHeight + offsetHeight)]))
    finalMesh:trimesh.Trimesh = trimesh.util.concatenate([baseMesh] + buildingMeshes)

    finalMesh.apply_scale(1000 / scale)
    finalMesh.export('output/mesh.stl')