import time
import json
from dotenv import load_dotenv
import os 
import base64
from requests import post, get
import urllib
from pathlib import Path
import webbrowser

env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path)

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

redirect_uri = "http://127.0.0.1:3000"
auth_url = "https://accounts.spotify.com/authorize"
api_base_url = "https://api.spotify.com/v1"
token_url = "https://accounts.spotify.com/api/token"

token_path = "/Users/franciscolopez/Documents/SpotifyProj/src/data/tokens.json"

print(client_id, client_secret)

# Function call to get token from Spotify API
def get_token():
    auth = client_id + ":" + client_secret
    auth_bytes = auth.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {"grant_type": "client_credentials"}

    result = post(token_url, headers=headers, data=data)

    json_res = json.loads(result.content)
    token = json_res["access_token"]

    return token

# Create auth token for API call
def get_auth_header(token):
    return {"Authorization": "Bearer " + token}



def user_auth():

    scope = 'user-read-private user-read-email'

    parameters = {
        "client_id": f"{client_id}",
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "scope": scope,
        "show_dialog": True
    }

    auth_url_set = f"{auth_url}?{urllib.parse.urlencode(parameters)}"

    webbrowser.open(auth_url_set)
    

def callback():
    code = "..."            
    req_body = {
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "client_secret": client_secret
    }

    res = post(token_url, data=req_body)
    
    token_info = res.json()
    # print(f"In Callback: token info = {token_info}")
    
    token_info["expires_in"] = int(time.time()) + token_info["expires_in"]

    # Save tokens to a file
    with open(token_path, "w") as f:
        json.dump(token_info, f)

    return token_info

def load_token(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def refresh_access_token(refresh_token):
    auth_header = base64.b64encode(f"client_id:{client_id}".encode()).decode()

    payload = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }

    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    res = post(token_url, data=payload, headers=headers)
    new_token = res.json()

    new_token["expires_in"] = int(time.time()) + new_token["expires_in"]
    if "refresh_token" not in new_token:
        new_token["refresh_token"] = refresh_token
    
    with open(token_path, "w") as f:
        json.dump(new_token, f)
    
    return new_token

def get_valid_token():
    token = load_token(token_path)
    # print(f"In get_valid_token: token = {token}")
    if not token:
        raise Exception("No tokens saved, run the auth flow first")

    if token.get("expires_in", 0) < time.time():
        print("Access token expired, refreshing with new")
        token = refresh_access_token(token["refresh_token"])
    
    return token["access_token"]


def get_user_info(token):
    header = get_auth_header(token)

    res = get(api_base_url + "/me/playlists", headers=header)
    user_info = res.json()

    return user_info
    

def main():
    # user_auth()
    # token_request = callback()
    # print(f"Token Request = {token_request}")


    access_token = get_valid_token()


    result = get_user_info(access_token)
    print(f"User result:\b{result}")

    # user_id = result["id"]
    # print(user_id)
    

    # token = get_token()
    # headers = get_auth_header(token)
    # print(f"token = {token}")

    # get user information (personal)
    # user_info = get_user_info(headers)
    # print(f"User Information:\n\t{user_info}")


    # result = search_for_artist(token, "The Marias")
    # print(result["name"])
    # artist_id = result["id"]

    # Call songs and r
    # songs = get_songs_by_artist(token, artist_id)
    # print(songs)


if __name__ == "__main__":
    main()



# Function calls at start to test out API
# Simple search to get artist information from name
# def search_for_artist(token, artist_name):
#     url = f"{api_base_url}/search"
#     headers = get_auth_header(token)

#     query = f"?q={artist_name}&type=artist&limit=1"
#     query_url = url + query
#     result = get(query_url, headers=headers)
#     json_result = json.loads(result.content)["artists"]["items"]

#     if len(json_result) == 0:
#         print(f"{artist_name} doesn't exist")
#         return None
#     return json_result[0]

# # Get the top 5 songs from each artist
# def get_songs_by_artist(token, artist_id):
#     url = f"{api_base_url}/artists/{artist_id}/top-tracks?country=US"
#     headers = get_auth_header(token)
#     result = get(url, headers=headers)
#     json_result = json.loads(result.content)["tracks"]

#     # for idx, song in enumerate(songs): 
#     #     print(f"{idx + 1}: {song['name']}")
#     return json_result