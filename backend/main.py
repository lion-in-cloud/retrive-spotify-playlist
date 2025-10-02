# main.py
import os, base64, secrets
from urllib.parse import urlencode
from fastapi import FastAPI, HTTPException
from fastapi import Cookie
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware 
import httpx
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")
FRONTEND_URL= os.getenv("FRONTEND_URL", "https://retrive-spotify-playlist.vercel.app")
SPOTIFY_ACCOUNTS = "https://accounts.spotify.com"
SPOTIFY_API = "https://api.spotify.com/v1"

if not CLIENT_ID or not CLIENT_SECRET or not REDIRECT_URI or not FRONTEND_URL:
    raise RuntimeError("Spotify credentials and FRONTEND_URL must be configured")

app = FastAPI()
allow_origin_regex = os.getenv(
    "ALLOWED_ORIGIN_REGEX",
    r"https://retrive-spotify-playlist-.*\.vercel\.app",
)

raw_origins = os.getenv("ALLOWED_ORIGINS")
if raw_origins:
    origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]
else:
    origins = [
        "http://localhost:5173",   # React(Vite)
        "http://127.0.0.1:5173",   # 念のため
        "https://retrive-spotify-playlist.vercel.app",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,    
    allow_origin_regex=allow_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def _basic_auth():
    raw = f"{CLIENT_ID}:{CLIENT_SECRET}".encode()
    return "Basic " + base64.b64encode(raw).decode()

@app.get("/login")
def login():
    state = secrets.token_urlsafe(16)
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": "playlist-read-private",
        "state": state,
    }
    url = f"{SPOTIFY_ACCOUNTS}/authorize?{urlencode(params)}"
    return RedirectResponse(url)

@app.get("/callback")
async def callback(code: str = None):
    if not code:
        raise HTTPException(400, "No code provided")

    # code → access_token 交換
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": _basic_auth()}
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
        }
        r = await client.post(f"{SPOTIFY_ACCOUNTS}/api/token", data=data, headers=headers)
        r.raise_for_status()
        tokens = r.json()

    access_token = tokens["access_token"]
    app.state.access_token = access_token

    # 自分のプレイリストを取得
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{SPOTIFY_API}/me/playlists",
                             headers={"Authorization": f"Bearer {access_token}"})
        r.raise_for_status()
        playlists = r.json()
    
    redirect = RedirectResponse(url=FRONTEND_URL)
    redirect.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="none"
    )

    return redirect


@app.get("/playlists")
async def get_playlists(access_token: str = Cookie(None)):
    if not access_token:
        raise HTTPException(401, "Not logged in")
    

    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"{SPOTIFY_API}/me/playlists",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        r.raise_for_status()
        playlists = r.json()

    simplified = [
        {
            "id": item["id"],
            "name": item["name"],
            "image": item["images"][0]["url"] if item["images"] else None
        }
        for item in playlists["items"]
    ]

    return JSONResponse(simplified)



@app.get("/playlist/{playlist_id}")
async def get_playlist_tracks(playlist_id: str, access_token: str = Cookie(None)):
    if not access_token:
        raise HTTPException(401, "Not logged in. Please go to /login first.")

    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"{SPOTIFY_API}/playlists/{playlist_id}/tracks",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        r.raise_for_status()
        tracks = r.json()
    simplified = [
        {
            "name": item["track"]["name"],
            "artists": ", ".join(a["name"] for a in item["track"]["artists"])
        }
        for item in tracks["items"] if item["track"]
    ]

    return JSONResponse(simplified)


