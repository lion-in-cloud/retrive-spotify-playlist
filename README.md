# Spotify Playlist Exporter

Full-stack sample that lets a user authenticate with Spotify, list playlists, and export tracks. The backend is a FastAPI service that handles the OAuth flow and talks to the Spotify Web API; the frontend is a Vite + React app that consumes those endpoints.

## Project structure

```
backend/   FastAPI application and Python dependencies
frontend/  React client created with Vite
```

## Prerequisites

- Python 3.13 (or compatible with FastAPI)
- Node.js 18+ and npm
- A Spotify developer account with a registered application
- (Optional) mkcert or another tool to generate local TLS certs if you want to serve HTTPS locally

## Backend setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Create a `.env` file in the repository root with your Spotify app credentials:

```
SPOTIFY_CLIENT_ID="your-client-id"
SPOTIFY_CLIENT_SECRET="your-client-secret"
```

Start the API (HTTP):

```bash
uvicorn backend.main:app --reload
```

If you generated certificates and want HTTPS at `https://127.0.0.1:8000`, add the flags:

```bash
uvicorn backend.main:app --reload \
  --ssl-certfile ../cert.pem \
  --ssl-keyfile ../key.pem
```

## Spotify application configuration

In the Spotify Developer Dashboard, add the following to **Redirect URIs**:

```
https://127.0.0.1:8000/callback
```

This value must match the `REDIRECT_URI` constant used by the backend. Update both places if you prefer a different host/port or use plain HTTP.

## Frontend setup

```bash
cd frontend
npm install
npm run dev
```

By default the client sends requests to `https://127.0.0.1:8000`. If you change the backend origin, adjust the URLs in `frontend/src/App.tsx` or introduce an environment variable for the base URL.

## Development tips

- Keep the backend virtual environment in place; recreate it if you move the project directory.
- Certificates (`cert.pem`, `key.pem`) are ignored by Git. Regenerate them if they are missing on new machines.
- The current frontend focuses on playlists and track export. Extend the FastAPI app with additional endpoints as needed (for example `/playlists` and `/playlist/{id}` to match the client requests).
