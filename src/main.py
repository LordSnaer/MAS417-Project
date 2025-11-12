import api
import twodtiles

apiKey = api.readKey()

sessionToken = api.createSession(apiKey, "roadmap")

twodtiles.fetchTile(apiKey, sessionToken, 16,34223,19688)