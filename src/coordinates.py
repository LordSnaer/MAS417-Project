import math

earthRadius = (6378137 + 6356752) / 2 # average of equatorial and polar radius in meters

class GlobalCoordinate:
    def __init__(self, latitude: float, longitude: float):
        if abs(latitude) > 90:
            raise ValueError("Latitude must be between -90 and 90 degrees.")
        if abs(longitude) > 180:
            raise ValueError("Longitude must be between -180 and 180 degrees.")
        self.latitude = latitude
        self.longitude = longitude

class LocalCoordinate:
    def __init__(self, x: float, y: float):
        if max(abs(x), abs(y)) > 10e6:
            raise ValueError("This program assumes that the earth is flat")
        self.x = x
        self.y = y
        self.diagonal = math.sqrt(x**2 + y**2)

def globalToLocal(coord1:GlobalCoordinate, coord2:GlobalCoordinate) -> LocalCoordinate:
    delta_lat = coord2.latitude - coord1.latitude
    delta_lon = coord2.longitude - coord1.longitude
    x = math.radians(delta_lon) * earthRadius * math.cos(math.radians((coord1.latitude + coord2.latitude) / 2))
    y = math.radians(delta_lat) * earthRadius
    return LocalCoordinate(x, y)

def localToGlobal(globalCoord:GlobalCoordinate, localCoord:LocalCoordinate) -> GlobalCoordinate:
    newLatitude = globalCoord.latitude + (localCoord.y / earthRadius) * (180 / math.pi)
    newLongitude = globalCoord.longitude + (localCoord.x / (earthRadius * math.cos(math.radians(globalCoord.latitude)))) * (180 / math.pi)
    return GlobalCoordinate(newLatitude, newLongitude)

class BoundingBox:
    def __init__(self, type = "center", Coord1:GlobalCoordinate = None, Coord2:GlobalCoordinate = None, width:float = None, height:float = None):
        if type == "center":
            if Coord1 is None or width <= 0 or height <= 0:
                raise ValueError("For 'center' type, provide Coord1, width and height.")
            self.bottomLeft = localToGlobal(Coord1, LocalCoordinate(-width/2, -height/2))
            self.topRight = localToGlobal(Coord1, LocalCoordinate(width/2, height/2))
            self.center = Coord1
            self.width = width
            self.height = height
        elif type == "corners":
            if Coord1 is None or Coord2 is None:
                raise ValueError("For 'corners' type, provide both Coord1 and Coord2.")
            self.bottomLeft = GlobalCoordinate(min(Coord1.latitude, Coord2.latitude), min(Coord1.longitude, Coord2.longitude))
            self.topRight = GlobalCoordinate(max(Coord1.latitude, Coord2.latitude), max(Coord1.longitude, Coord2.longitude))
            self.center = GlobalCoordinate((self.bottomLeft.latitude + self.topRight.latitude) / 2, (self.bottomLeft.longitude + self.topRight.longitude) / 2)
            size = globalToLocal(self.bottomLeft, self.topRight)
            self.width = size.x
            self.height = size.y
        else:
            raise ValueError("Type must be either 'center' or 'corners'.")
