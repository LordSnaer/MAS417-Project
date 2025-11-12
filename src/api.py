import requests

def readKey():
    try: 
        apiFile = open("api_key.txt", "r")
        apiKey = apiFile.read()
        apiFile.close()
        if len(apiKey) != 39:
            print("api key not valid")
            exit(1)
        else:
            return apiKey
    except FileNotFoundError:
        print("Could not read API key from file. Make sure 'api_key.txt' exists.")
        exit(1)

def  createSession(apiKey, mapType):
    url = f"https://tile.googleapis.com/v1/createSession?key={apiKey}"
    data = {
        "mapType": mapType,
        "language": "en-US",
        "region": "NO"
    }
    header = {
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=data, headers=header)
    if response.status_code == 200:
        return response.json().get("session")
    else:
        print("Error creating session:", response.text)
        return None