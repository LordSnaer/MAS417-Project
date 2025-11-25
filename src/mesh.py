from . import coordinates as c
import math
import numpy as np
import stl
from shapely.geometry import Polygon
from shapely.ops import triangulate
import json

class BuildingPart:
    def __init__(self, nodes:list, minHeight:float, height:float, roofShape:str, roofHeight:float):
        self.nodes = nodes
        self.minHeight = minHeight
        self.height = height
        self.roofShape = roofShape
        self.roofHeight = roofHeight

nodeDict = {}
buildingPartDict = {}

def jsonParser(json, bbox:c.BoundingBox):
    for element in json["elements"]:
        if element["type"] == "node":
            nodeDict[element["id"]] = c.globalToLocal(bbox.center, c.GlobalCoordinate(latitude=element["lat"], longitude=element["lon"]))
        elif element["type"] == "way" and element["tags"]["building:part"] == "yes":
            tags = element["tags"]
            buildingPartDict[element["id"]] = BuildingPart(
                nodes = element["nodes"],
                minHeight = float(tags.get("min_height", 0)),
                height = float(tags.get("height", 10)),
                roofShape = tags.get("roof:shape", "flat"),
                roofHeight = float(tags.get("roof:height", 0))
            )
    
def meshGeneration(bbox:c.BoundingBox, scale: float, json):
    jsonParser(json, bbox)
