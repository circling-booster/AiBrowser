import React, { useEffect, useState } from 'react';

const API_BASE = "http://127.0.0.1:5000";

function App() {
  const [plugins, setPlugins] = useState({});
  const [status, setStatus] = useState("Checking...");

  useEffect(() => {
    fetchPlugins();
    checkHealth();
  }, []);

  const checkHealth = async () => {
    try {
      await fetch(API_BASE);
      setStatus("Online (Python Backend Connected)");
    } catch {
      setStatus("Offline (Backend Failed)");
    }
  };

  const fetchPlugins = async () => {
    const res = await fetch(`${API_BASE}/plugins`);
    const data = await res.json();
    setPlugins(data);
  };

  const togglePlugin = async (id, currentState) => {
    await fetch(`${API_BASE}/plugins/${id}/toggle?active=${!currentState}`, { method: "POST" });
    fetchPlugins(); // 리스트 갱신
  };

  return (
    <div style={{ padding: 20, fontFamily: 'sans-serif' }}>
      <h1>🤖 AI Automation Platform</h1>
      <div style={{ padding: 10, background: '#eee', marginBottom: 20 }}>
        Status: <strong>{status}</strong>
      </div>

      <h2>Installed Modules</h2>
      <div style={{ display: 'grid', gap: '10px' }}>
        {Object.entries(plugins).map(([id, p]) => (
          <div key={id} style={{ border: '1px solid #ccc', padding: 15, borderRadius: 8 }}>
            <h3>{p.info.name} <small>v{p.info.version}</small></h3>
            <p>{p.info.description}</p>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <label>
                <input 
                  type="checkbox" 
                  checked={p.active} 
                  onChange={() => togglePlugin(id, p.active)} 
                />
                Activate Feature
              </label>
              {p.active && <span style={{ color: 'green' }}>● Running</span>}
            </div>
          </div>
        ))}
      </div>
      
      <div style={{ marginTop: 30 }}>
        <button onClick={() => window.electronAPI.openProxyBrowser()}>
            🌐 Launch with Proxy (Native Browser)
        </button>
      </div>
    </div>
  );
}

export default App;