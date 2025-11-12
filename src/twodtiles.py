import requests

def fetchTile(apiKey, sessionToken, zoom, x, y):
    url = f"https://tile.googleapis.com/v1/2dtiles/{zoom}/{x}/{y}?session={sessionToken}&key={apiKey}&orientation=0"
    response = requests.get(url)
    if response.status_code == 200:
        tileData = response.content
        with open(f"output/tile_{zoom}_{x}_{y}.png", "wb") as file:
            file.write(tileData)
        print(f"Tile saved: output/tile_{zoom}_{x}_{y}.png")
    else:
        print("Error fetching tile:", response.text)



