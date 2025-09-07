from flask import Flask, request
import os, requests, json
from requests.auth import HTTPBasicAuth
from replit import db


def getTrack(year):
  clientID = os.environ['CLIENT_ID']
  clientSecret = os.environ['CLIENT_SECRET']
  
  url = "https://accounts.spotify.com/api/token"
  data = {"grant_type":"client_credentials"}
  auth = HTTPBasicAuth(clientID, clientSecret)
  
  response = requests.post(url, data=data, auth=auth)
  if response.status_code == 200:
    accessToken = response.json()["access_token"]
    print("Successfully logged in to Spotify")
  else:
    print(f"Login failed: {response.status_code}")
    exit(1)
  
  
  offset = 0
  try:
    offset = db[year]
    if offset >200:
      db[year] = 0
    db[year] += 10
  except:
    db[year]=10
  
  headers = {"Authorization": f"Bearer {accessToken}"}
  search_url = "https://api.spotify.com/v1/search"
  search = f"?q=artist%3A{year}&type=track&limit=5&offset={offset}"
  
  full_url = f"{search_url}{search}"
  
  response = requests.get(full_url, headers=headers)
  data = response.json()

  songs = ""
  f = open("songs.html", "r")
  songs = f.read()
  f.close()

  listSongs = ""
  
  
  for track in data["tracks"]["items"]:
    thisTrack = songs
    thisTrack = thisTrack.replace("{name}",f"""{track["name"]}""")
    thisTrack = thisTrack.replace("{url}", track["preview_url"] or "No preview available")
    if track["preview_url"]:
        thisTrack = thisTrack.replace("{url}", track["preview_url"])
        listSongs += thisTrack
    else:
      # For tracks without previews, show just the name without audio player
      listSongs += f"<h2>{track['name']}</h2><p><em>No preview available</em></p><hr>"

  return listSongs


app = Flask(__name__)

@app.route("/", methods=["POST"])
def change():
  page = ""
  f = open("form.html", "r")
  page = f.read()
  f.close()
  year = request.form["year"]
  songs = getTrack(year)
  page = page.replace("{songs}", songs)
  page = page.replace("{value}", year)
  return page


@app.route("/")
def index():
  page = ""
  f = open("form.html")
  page = f.read()
  f.close()
  page = page.replace("{songs}", "")
  page = page.replace("{value}", "1990")
  return page


app.run(host='0.0.0.0', port=81)
  
