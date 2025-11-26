from unittest import case
from . import coordinates as c
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

class Way:
    polygon:geometry.Polygon
    def __init__(self, nodes:list, minHeight:float, height:float, roofShape:str, roofHeight:float, roofOrientation:str, type:str):
        self.nodes = nodes
        self.minHeight = minHeight
        self.height = height
        self.roofShape = roofShape
        self.roofHeight = roofHeight
        self.roofOrientation = roofOrientation
        self.type = type
nodeDict = {}
wayDict = {}

def jsonParser(response:dict, bbox:c.BoundingBox) -> None:
    for element in response["elements"]:
        if element["type"] == "node":
            nodeDict[element["id"]] = c.globalToLocal(bbox.center, c.GlobalCoordinate(latitude=element["lat"], longitude=element["lon"]))
        elif element["type"] == "way":
            tags:dict = element["tags"]
            wayDict[element["id"]] = Way(
                nodes = element["nodes"],
                minHeight = float(tags.get("min_height", defaultMinHeight)),
                height = float(tags.get("height", defaultHeight)),
                roofShape = tags.get("roof:shape", defaultRoofShape),
                roofOrientation = tags.get("roof:orientation", ""),
                roofHeight = float(tags.get("roof:height", defaultRoofHeight)),
                type = ("building" if "building" in tags else ("part" if tags.get("building:part")=="yes" else ""))
            )
            if "levels" in tags and "height" not in tags:
                wayDict[element["id"]].height = int(tags["levels"]) * defaultFloorHeight

def roofMesh(way:Way) -> trimesh.Trimesh:
    match way.roofShape:
        case "flat":
            return None
        case "gabled":
            nodes = [nodeDict[nodeId] for nodeId in way.nodes]
            vertices = [[node.x, node.y, 0] for node in nodes]
            return None #temporarily disabled so the code runs
            direction = 'x' if c.distance(nodes[0], nodes[1]).diagonal > c.distance(nodes[1], nodes[2]).diagonal else 'y'
            if (way.roofOrientation == "across" and direction == 'x') or (way.roofOrientation != "across" and direction == 'y'):
                ridge = np.array([
                    [(nodes[0].x + nodes)/2, miny, way.roofHeight],
                    [(minx + maxx)/2, maxy, way.roofHeight]
                ])
            else:
                ridge = np.array([
                    [minx, (miny + maxy)/2, way.roofHeight],
                    [maxx, (miny + maxy)/2, way.roofHeight]  
                ])
            left = trimesh.Trimesh(vertices=[
                [minx, miny, 0], 
                [minx, maxy, 0], 
                ridge[0]
            ], faces=[[0,1,2]])
            right = trimesh.Trimesh(vertices=[
                [maxx, miny, 0], 
                [maxx, maxy, 0], 
                ridge[1]
            ], faces=[[0,1,2]])

            return trimesh.util.concatenate([left, right])
        case "skillion":
            return None
        case "half-hipped":
            return None
        case "hipped":
            return None
        case "pyramidal":
            nodes = [nodeDict[nodeId] for nodeId in way.nodes]
            bottomVertices = [[node.x, node.y, 0] for node in nodes]
            apex = [way.polygon.centroid.x, way.polygon.centroid.y, way.roofHeight]
            baseFaces = trimesh.creation.triangulate_polygon(way.polygon)
            pyramidFaces = [
                trimesh.Trimesh(
                    vertices=[
                        bottomVertices[i],
                        bottomVertices[(i + 1) % len(bottomVertices)],
                        apex
                    ], faces=[[0,1,2]]
                ) for i in range(len(bottomVertices))
            ]
            return trimesh.util.concatenate([baseFaces] + pyramidFaces)

        case "gambrel":
            return None
        case "mansard":
            return None
        case "dome":
            return None
        case "onion":
            return None
        case "saltbox":
            return None
        case _:
            return None
        

def meshGeneration(bbox:c.BoundingBox, scale:float, response:dict) -> None:
    jsonParser(response, bbox)
    xmin = - bbox.width / 2
    ymin = - bbox.height / 2
    xmax = bbox.width / 2
    ymax = bbox.height / 2
    basePolygon = geometry.Polygon().from_bounds(xmin, ymin, xmax, ymax)
    #create polygons for each way and remove those not fully within bounding box
    waysToRemove = []
    for id, way in wayDict.items():
        footprint = [nodeDict[nodeId].xy for nodeId in way.nodes]
        way.polygon = geometry.Polygon(footprint)
        if not basePolygon.contains(way.polygon):
            waysToRemove.append(id)
    for id in waysToRemove:
        wayDict.pop(id)
    waysToRemove.clear()
    #remove buildings that have building parts overlapping them]
    for partID in [id for id in list(wayDict.keys()) if wayDict[id].type == "part"]:
        for buildingID in [id for id in list(wayDict.keys()) if wayDict[id].type == "building"]:
            if buildingID not in waysToRemove and wayDict[buildingID].polygon.intersects(wayDict[partID].polygon):
                waysToRemove.append(buildingID)
    for id in waysToRemove:
            wayDict.pop(id)
    
    baseMesh = trimesh.creation.extrude_polygon(basePolygon, defaultBaseHeight)
    buildingMeshes = []
    for id, way in wayDict.items():
        wallHeight = way.height - way.minHeight - way.roofHeight
        offsetHeight = way.minHeight + defaultBaseHeight
        if wallHeight > 0:
            buildingMeshes.append(trimesh.creation.extrude_polygon(way.polygon, wallHeight).apply_translation([0, 0, offsetHeight]))
        roof = roofMesh(way)
        if roof is not None:
            buildingMeshes.append(roof.apply_translation([0, 0, (wallHeight + offsetHeight)]))
    finalMesh:trimesh.Trimesh = trimesh.util.concatenate([baseMesh] + buildingMeshes)

    finalMesh.apply_scale(1000 / scale)
    finalMesh.export('output/mesh.stl')