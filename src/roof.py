import math
import numpy as np
from shapely import geometry, ops
import trimesh
from . import (
    coordinates as c,
    elements as e
)

def gabledRoof(way:e.Way) -> trimesh.Trimesh:
    polygon = way.polygon.minimum_rotated_rectangle
    nodes = [c.LocalCoordinate(x, y) for x, y in list(polygon.exterior.coords)[:-1]]
    baseVertices = [[node.x, node.y, 0] for node in nodes]
    refDirection = '-xy' if c.distance(nodes[0], nodes[1]).diagonal > c.distance(nodes[1], nodes[2]).diagonal else 'xy'
    direction = "xy" if (way.roofOrientation == "across" and refDirection == '-xy') or (way.roofOrientation != "across" and refDirection == 'xy') else "-xy"
    ridgepoint = [
        c.midpoint(nodes[0], nodes[1]),
        c.midpoint(nodes[2], nodes[3])
    ] if direction == "xy" else [
        c.midpoint(nodes[0], nodes[3]),
        c.midpoint(nodes[2], nodes[1])
    ]
    ridgeVertices = [[p.x, p.y, way.roofHeight] for p in ridgepoint]
    
    baseFaces = [trimesh.creation.triangulate_polygon(polygon)]
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

# def chatSkillionRoof(way:e.Way) -> trimesh.Trimesh:
#     # Create a single-slope roof by raising vertices along a direction.
#     # Use roof:direction if present (cardinal or degrees), otherwise fall back to longest axis.
#     if not hasattr(way, "polygon") or way.polygon is None:
#         nodes = [e.nodeDict[nodeId] for nodeId in way.nodes]
#         coords = [(n.x, n.y) for n in nodes]
#     else:
#         coords = list(way.polygon.exterior.coords)[:-1]

#     if len(coords) < 3:
#         return None

#     # bounding box & centroid
#     xs = [p[0] for p in coords]
#     ys = [p[1] for p in coords]
#     minx, maxx = min(xs), max(xs)
#     miny, maxy = min(ys), max(ys)
#     cx = (minx + maxx) / 2.0
#     cy = (miny + maxy) / 2.0
#     rangex = maxx - minx
#     rangey = maxy - miny

#     # determine direction vector (dx, dy) from roof:direction if provided
#     dx = dy = None
#     used_cardinal = False
#     dir_tag = getattr(way, "roofDirection", "").strip() if hasattr(way, "roofDirection") else ""
#     if dir_tag:
#         # try numeric degrees (bearing clockwise from North)
#         try:
#             deg = float(dir_tag)
#             rad = math.radians(deg)
#             # bearing -> vector: dx = sin(deg), dy = cos(deg)
#             dx = math.sin(rad)
#             dy = math.cos(rad)
#         except Exception:
#             # cardinal mapping but aligned to building: compute building principal axis (PCA)
#             used_cardinal = True
#             try:
#                 pts = np.array(coords)
#                 # get covariance and principal eigenvector
#                 cov = np.cov(pts.T)
#                 eigvals, eigvecs = np.linalg.eigh(cov)
#                 # principal axis = eigenvector with largest eigenvalue
#                 principal = eigvecs[:, np.argmax(eigvals)]
#                 px, py = float(principal[0]), float(principal[1])
#                 # normalize principal
#                 norm_p = math.hypot(px, py)
#                 if norm_p == 0:
#                     px, py = 1.0, 0.0
#                 else:
#                     px /= norm_p; py /= norm_p
#                 # perpendicular axis
#                 perp_x, perp_y = -py, px
#             except Exception:
#                 # fallback axes if PCA fails
#                 px, py = (1.0, 0.0)
#                 perp_x, perp_y = (0.0, 1.0)

#             m = dir_tag.upper()
#             # decide on vector from cardinal, but align to building axes:
#             # N/S -> use principal axis (px,py) oriented by N(+y)/S(-y)
#             # E/W -> use perpendicular axis (perp_x,perp_y) oriented by E(+x)/W(-x)
#             if all(ch in "NS" for ch in m):  # N or S
#                 base_x, base_y = px, py
#                 if "N" in m and base_y < 0:
#                     base_x, base_y = -base_x, -base_y
#                 if "S" in m and base_y > 0:
#                     base_x, base_y = -base_x, -base_y
#                 dx, dy = base_x, base_y
#             elif all(ch in "EW" for ch in m):  # E or W
#                 base_x, base_y = perp_x, perp_y
#                 if "E" in m and base_x < 0:
#                     base_x, base_y = -base_x, -base_y
#                 if "W" in m and base_x > 0:
#                     base_x, base_y = -base_x, -base_y
#                 dx, dy = base_x, base_y
#             else:
#                 # diagonals like NE, SW: combine principal and perp with signs
#                 sign_y = 1 if "N" in m else -1 if "S" in m else 0
#                 sign_x = 1 if "E" in m else -1 if "W" in m else 0
#                 comb_x = sign_y * px + sign_x * perp_x
#                 comb_y = sign_y * py + sign_x * perp_y
#                 norm_c = math.hypot(comb_x, comb_y)
#                 if norm_c == 0:
#                     dx, dy = px, py
#                 else:
#                     dx, dy = comb_x / norm_c, comb_y / norm_c

#     # fallback: choose principal axis along longer extent (positive x or positive y)
#     if dx is None or dy is None:
#         if rangex >= rangey:
#             dx, dy = 1.0, 0.0
#         else:
#             dx, dy = 0.0, 1.0

#     # If the direction came from a cardinal tag, rotate the vector
#     # 90° counter-clockwise to correct the 90° clockwise misalignment.
#     if used_cardinal:
#         dx, dy = -dy, dx

#         # Snap roof so the bottom-most polygon edge becomes collinear with the low side.
#         # Find edges where both vertices project near the minimum projection and make the
#         # roof slope direction perpendicular to that edge (use longest such edge).
#         try:
#             projs_tmp = [(p[0]*dx + p[1]*dy) for p in coords]
#             minproj = min(projs_tmp)
#             bottom_edges = []
#             for i in range(len(coords)):
#                 p_i = projs_tmp[i]
#                 p_j = projs_tmp[(i + 1) % len(coords)]
#                 if abs(p_i - minproj) < 1e-6 and abs(p_j - minproj) < 1e-6:
#                     bottom_edges.append((coords[i], coords[(i + 1) % len(coords)]))
#             if bottom_edges:
#                 best_vx = best_vy = 0.0
#                 best_len = 0.0
#                 for a, b in bottom_edges:
#                     vx = b[0] - a[0]; vy = b[1] - a[1]
#                     l = math.hypot(vx, vy)
#                     if l > best_len:
#                         best_len = l
#                         best_vx, best_vy = vx, vy
#                 if best_len > 0:
#                     # slope direction should be perpendicular to the bottom edge
#                     ndx = -best_vy / best_len
#                     ndy = best_vx / best_len
#                     # keep same general orientation as initial dx,dy
#                     if ndx * dx + ndy * dy < 0:
#                         ndx, ndy = -ndx, -ndy
#                     dx, dy = ndx, ndy
#         except Exception:
#             # fallback: keep the cardinal-corrected vector
#             pass

#     # normalize direction vector
#     norm = math.hypot(dx, dy)
#     if norm == 0:
#         dx, dy = 1.0, 0.0
#     else:
#         dx /= norm
#         dy /= norm

#     # FIX: rotate skillions by 180° (they were reversed) => flip vector
#     dx, dy = -dx, -dy

#     # compute projection range for all polygon coords
#     projs = [ (p[0]*dx + p[1]*dy) for p in coords ]
#     minp, maxp = min(projs), max(projs)
#     if maxp - minp == 0:
#         # degenerate; no slope
#         def z_for_point(pt): return 0.0
#     else:
#         def z_for_point(pt):
#             p = pt[0]*dx + pt[1]*dy
#             t = (p - minp) / (maxp - minp)
#             return way.roofHeight * t

#     # triangulate and lift vertices
#     try:
#         poly = way.polygon if hasattr(way, "polygon") and way.polygon is not None else geometry.Polygon(coords)
#         tris = ops.triangulate(poly)
#     except Exception:
#         return None

#     vertices = []
#     faces = []
#     for tri in tris:
#         tri_coords = list(tri.exterior.coords)[:3]
#         idx0 = len(vertices)
#         for pt in tri_coords:
#             vertices.append([pt[0], pt[1], z_for_point(pt)])
#         faces.append([idx0, idx0+1, idx0+2])

#     if not vertices or not faces:
#         return None

#     # build mesh
#     m = trimesh.Trimesh(vertices=np.array(vertices), faces=np.array(faces))

#     # Snap XY to footprint vertices/edges and recompute Z where appropriate
#     try:
#         _snap_mesh_vertices_to_footprint(m, coords, z_for_point, dx=dx, dy=dy, minp=minp, tol_xy=1e-1, tol_edge=1e-6)
#     except Exception:
#         pass

#     # ensure base minimum Z is exactly 0 (translate even if tiny negative/positive)
#     try:
#         min_z = float(m.vertices[:, 2].min())
#         if math.isfinite(min_z) and abs(min_z) > 0.0:
#             m.apply_translation([0.0, 0.0, -min_z])
#     except Exception:
#         pass

#     return m

def skillionRoof(way:e.Way) -> trimesh.Trimesh:
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
    return None #temporarily disabled so the code runs
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

