from shapely import geometry
import trimesh
from . import (
    coordinates as c,
    elements as e
)

def gabledRoof(way:e.Way) -> trimesh.Trimesh:
    polygon = way.polygon.minimum_rotated_rectangle
    nodes = [c.LocalCoordinate(x, y) for x, y in list(polygon.exterior.coords)[:-1]]
    baseVertices = [[node.x, node.y, 0] for node in nodes]
    refDirection = '-xy' if c.Distance(nodes[0], nodes[1]).diagonal > c.Distance(nodes[1], nodes[2]).diagonal else 'xy'
    direction = "xy" if (way.roofOrientation == "across" and refDirection == '-xy') or (way.roofOrientation != "across" and refDirection == 'xy') else "-xy"
    ridgepoint = [
        c.midpoint(nodes[0], nodes[1]),
        c.midpoint(nodes[2], nodes[3])
    ] if direction == "xy" else [
        c.midpoint(nodes[0], nodes[3]),
        c.midpoint(nodes[2], nodes[1])
    ]
    ridgeVertices = [[p.x, p.y, way.roofHeight] for p in ridgepoint]
    
    baseFaces = [
        trimesh.Trimesh(
            vertices=[vertex for vertex in baseVertices],
            faces=[[0,1,2], [0,2,3]]
        )
    ]
    gableFaces = [
        trimesh.Trimesh(
            vertices=[
                baseVertices[0],
                baseVertices[1 if direction == "xy" else 3],
                ridgeVertices[0]
            ],
            faces=[[0,1,2]]
        ),
        trimesh.Trimesh(
            vertices=[
                baseVertices[2],
                baseVertices[3 if direction == "xy" else 1],
                ridgeVertices[1]
            ], faces=[[0,1,2]]
        )
    ]
    slopeFaces = [
        trimesh.Trimesh(
            vertices=[
                baseVertices[1 if direction == "xy" else 3],
                baseVertices[2],
                ridgeVertices[1],
                ridgeVertices[0]
            ], faces=[[0,1,2], [0,2,3]]
        ),
        trimesh.Trimesh(
            vertices=[
                baseVertices[3 if direction == "xy" else 1],
                baseVertices[0],
                ridgeVertices[0],
                ridgeVertices[1]
            ], faces=[[0,1,2], [0,2,3]]
        )
    ]
    return trimesh.util.concatenate(baseFaces + gableFaces + slopeFaces)

def skillionRoof(way:e.Way) -> trimesh.Trimesh:
    return None #temporarily disabled so the code runs
    polygon = way.polygon.minimum_rotated_rectangle
    baseFaces = trimesh.creation.triangulate_polygon(polygon)
    [S, W, N, E] = [c.LocalCoordinate(x, y) for x, y in list(polygon.exterior.coords)[:-1]]
    basevertices = [[node.x, node.y, 0] for node in [S, W, N, E]]
    if way.roofDirection in ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]:
        direction = way.roofDirection
    else:
        try:
            dir = float(way.roofDirection) % 360
        except ValueError:
            dir = "N"
        if 22.5 <= dir < 67.5:
            direction = "NE"
        elif 67.5 <= dir < 112.5:
            direction = "E"
        elif 112.5 <= dir < 157.5:
            direction = "SE"
        elif 157.5 <= dir < 202.5:
            direction = "S"
        elif 202.5 <= dir < 247.5:
            direction = "SW"
        elif 247.5 <= dir < 292.5:
            direction = "W"
        elif 292.5 <= dir < 337.5:
            direction = "NW"
        else:
            direction = "N"
    if len(direction) == 2:
        lowPoints = [direction[0], direction[1]]
    else:
        lowPoints = [direction]
        clockwise = True if N.x > S.x else False
        match direction:
            case "N":
                lowPoints.append("E" if clockwise else "W")
            case "E":
                lowPoints.append("S" if clockwise else "N")
            case "S":
                lowPoints.append("W" if clockwise else "E")
            case "W":
                lowPoints.append("N" if clockwise else "S")

    slopeFaces = trimesh.creation.triangulate_polygon(geometry.Polygon(

    ))

def pyramidRoof(way:e.Way) -> trimesh.Trimesh: # don't touch this. It works
    nodes = [e.nodeDict[nodeId] for nodeId in way.nodes]
    bottomVertices = [[node.x, node.y, 0] for node in nodes]
    apex = [way.polygon.centroid.x, way.polygon.centroid.y, way.roofHeight]
    pyramidFaces = [
        trimesh.Trimesh(
            vertices=[
                bottomVertices[i],
                bottomVertices[(i + 1) % len(bottomVertices)],
                apex
            ], faces=[[0,1,2]]
        ) for i in range(len(bottomVertices))
    ]
    return trimesh.util.concatenate(pyramidFaces)

def roofMesh(way:e.Way) -> trimesh.Trimesh:
    match way.roofShape:
        case "flat":
            roof = None
        case "gabled":
            roof = gabledRoof(way)
        case "skillion":
            roof = skillionRoof(way)
        case "half-hipped":
            roof = None
        case "hipped":
            roof = gabledRoof(way)  # Temporary substitution
        case "pyramidal":
            roof = pyramidRoof(way)
        case "gambrel":
            roof = None
        case "mansard":
            roof = None
        case "dome":
            roof = None
        case "onion":
            roof = None
        case "saltbox":
            roof = None
        case _:
            roof = None
    return roof if roof is not None else None

