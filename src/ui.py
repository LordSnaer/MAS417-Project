from . import coordinates as c
import sys

exampleLocations = {
    "Nidarosdomen": (
        c.GlobalCoordinate(63.426619, 10.395700),
        c.GlobalCoordinate(63.427257, 10.398082)
    ),
    "Kristiansand domkirke": (
        c.GlobalCoordinate(58.145923, 7.994083),
        c.GlobalCoordinate(58.146344, 7.995170)
    ),
    "Palace of Westminster (Big Ben)": (
        c.GlobalCoordinate(51.498034, -0.126185),
        c.GlobalCoordinate(51.500831, -0.123484)
    )
}

def boundingBoxDialog() -> c.BoundingBox:
    if input("Use example locations? (y/N): ").strip().lower() == 'y':
        print("Available example locations:")
        for i, key in enumerate(exampleLocations.keys()):
            print(f"{i+1}: {key}")
        choice = int(input(f"Select a location by number (1-{len(exampleLocations)}):")) - 1
        if choice < 0 or choice >= len(exampleLocations):
            raise ValueError("Invalid choice")
        else:
            coord1, coord2 = exampleLocations[list(exampleLocations.keys())[choice]]
            return c.BoundingBox(type="corners", Coord1=coord1, Coord2=coord2)
    else:
        print("1: define a rectangle by center coordinate and width/height in meters, or")
        print("2: define a rectangle by coordinates of two corners")
        choice = input ("Enter a number (1/2): ").strip()
        match choice:
            case '1':
                lat = float(input("Enter center latitude: "))
                lon = float(input("Enter center longitude: "))
                width = float(input("Enter width in meters: "))
                height = float(input("Enter height in meters: "))
                centerCoord = c.GlobalCoordinate(lat, lon)
                return c.BoundingBox(type="center", Coord1=centerCoord, width=width, height=height)
            case '2':
                lat1 = float(input("Enter latitude 1: "))
                lon1 = float(input("Enter longitude 1: "))
                lat2 = float(input("Enter latitude 2: "))
                lon2 = float(input("Enter longitude 2: "))
                coord1 = c.GlobalCoordinate(lat1, lon1)
                coord2 = c.GlobalCoordinate(lat2, lon2)
                return c.BoundingBox(type="corners", Coord1=coord1, Coord2=coord2)
            case _:
                raise ValueError("Invalid choice. Please enter '1' or '2'.")
            
def scaleDialog() -> float:
    scale = input("Enter scale factor (default is 1000): ").strip()
    if scale == "":
        return 1000.0
    try:
        scaleValue = float(scale)
        if scaleValue <= 0:
            raise ValueError("Scale factor must be positive.")
        return scaleValue
    except ValueError:
        print("Invalid input. Please enter a numeric value for scale factor.")
        sys.exit(1)

def savePathDialog() -> str:
    path = input("Enter output STL file path (default is ./output/buildings.stl): ").strip()
    return path