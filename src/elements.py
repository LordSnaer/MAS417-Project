from shapely import geometry

class Way:
    polygon:geometry.Polygon
    def __init__(self, nodes:list, minHeight:float, height:float, roofShape:str, roofHeight:float, roofOrientation:str, type:str, roofDirection:str=""):
        self.nodes = nodes
        self.minHeight = minHeight
        self.height = height
        self.roofShape = roofShape
        self.roofHeight = roofHeight
        self.roofOrientation = roofOrientation
        self.roofDirection = roofDirection
        self.type = type

nodeDict = {}
wayDict = {}