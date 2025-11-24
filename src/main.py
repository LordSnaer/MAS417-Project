import overpass_api
import json
import coordinates as c

#kristiansand domkirke
# coord1 = c.GlobalCoordinate(58.145923, 7.994083)
# coord2 = c.GlobalCoordinate(58.146344, 7.995170)

#nidarosdomen
coord1 = c.GlobalCoordinate(63.426619, 10.395700)
coord2 = c.GlobalCoordinate(63.427257, 10.398082)

bbox = c.BoundingBox(type="corners", Coord1=coord1, Coord2=coord2)

response = overpass_api.query(bbox)

with open("output/overpass_result.json", "w") as f:
    json.dump(response, indent=4, fp=f)
