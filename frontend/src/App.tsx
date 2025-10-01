import "./App.css";
import { useState, useEffect } from "react";


type Playlist = {
  id: string;
  name: string;
  image: string | null;
};

type Track = {
  name: string;
  artists: string;
  url: string;
};

function App() {
  const [playlists, setPlaylists] = useState<Playlist[]>([]);
  const [tracks, setTracks] = useState<Track[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const API = import.meta.env.VITE_API_BASE_URL;

  useEffect(() => {
    fetch(`${API}/playlists`, { credentials: "include" })
      .then((res) => res.json())
      .then((data) => setPlaylists(data));
  }, []);

  const loadTracks = (playlistId: string) => {
    setSelected(playlistId);
    fetch(`${API}/playlist/${playlistId}`, { credentials: "include" })
      .then((res) => res.json())
      .then((data) => setTracks(data));
  };

  const downloadCSV = () => {
    const header = "Title,Artists,URL\n";
    const rows = tracks
      .map((t) => `"${t.name}","${t.artists}","${t.url}"`)
      .join("\n");
    const blob = new Blob([header + rows], { type: "text/csv" });
    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = "playlist.csv";
    a.click();
    URL.revokeObjectURL(url);
  };
  const login = () => {
  window.location.href = `${API}/login`;
  };

return (
  <div className="app">
    <div className="header">
      <h1>My Spotify Playlists</h1>
      <div className="actions">
        <button className="btn primary" onClick={() => (window.location.href = API + "/login")}>
          Login with Spotify
        </button>
        {selected && (
          <>
            <button className="btn" onClick={() => setSelected(null)}>← Back</button>
            <button className="btn" onClick={downloadCSV}>Download CSV</button>
          </>
        )}
      </div>
    </div>

    {/* プレイリスト一覧 */}
    {!selected && (
      <>
        {Array.isArray(playlists) && playlists.length ? (
          <div className="grid">
            {playlists.map((pl) => (
              <div key={pl.id} className="panel card" onClick={() => loadTracks(pl.id)}>
                {pl.image && <img className="thumb" src={pl.image} alt={pl.name} />}
                <div className="meta">
                  <p className="title">{pl.name}</p>
                  {/* <p className="sub">nn tracks</p> ← もし欲しければサーバ側で曲数も返して表示 */}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="panel empty mt-16">Login and refresh to load your playlists.</div>
        )}
      </>
    )}

    {/* トラック一覧 */}
    {selected && (
      <div className="panel mt-16">
        <div className="toolbar">
          <span className="sub">Tracks</span>
        </div>
        <div className="list">
          {tracks.map((t, i) => (
            <div key={i} className="row">
              <a className="name" href={t.url} target="_blank" rel="noreferrer">{t.name}</a>
              <span className="artists">{t.artists}</span>
            </div>
          ))}
        </div>
      </div>
    )}
  </div>
);
}

export default App;
