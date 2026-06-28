import { useEffect, useState } from 'react';

const API_BASE = 'http://localhost:8000/api';

function App() {
  const [source, setSource] = useState('Modern Loft | $2400 | 2 | 2 | 1100 | Downtown | Pet friendly and renovated');
  const [listings, setListings] = useState([]);
  const [status, setStatus] = useState('Loading listings...');

  async function loadListings() {
    const response = await fetch(`${API_BASE}/listings`);
    const data = await response.json();
    setListings(data);
    setStatus(data.length ? `Loaded ${data.length} listings.` : 'No listings yet.');
  }

  useEffect(() => {
    loadListings();
  }, []);

  async function handleImport(event) {
    event.preventDefault();
    setStatus('Importing...');
    const response = await fetch(`${API_BASE}/listings/import`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ source })
    });
    const result = await response.json();
    if (response.ok) {
      setStatus(`Imported ${result.imported} listing(s).`);
      setSource('');
      await loadListings();
    } else {
      setStatus(result.detail || 'Import failed.');
    }
  }

  async function handleClear() {
    await fetch(`${API_BASE}/listings`, { method: 'DELETE' });
    await loadListings();
    setStatus('Cleared.');
  }

  const averageScore = listings.length
    ? (listings.reduce((sum, item) => sum + (item.score || 0), 0) / listings.length).toFixed(1)
    : '0.0';

  return (
    <main>
      <section className="card hero">
        <h1>RowKey OS / Project Titan</h1>
        <p>Phase 1 MVP for manual listing import, scoring, and a simple decision dashboard.</p>
      </section>

      <section className="card">
        <h2>Import listings</h2>
        <form onSubmit={handleImport}>
          <textarea
            value={source}
            onChange={(event) => setSource(event.target.value)}
            placeholder="Title | Price | Bedrooms | Bathrooms | Sq Ft | Neighborhood | Notes"
          />
          <div className="actions">
            <button type="submit">Import</button>
            <button type="button" className="secondary" onClick={handleClear}>Clear</button>
          </div>
        </form>
        <p className="status">{status}</p>
      </section>

      <section className="card">
        <h2>Dashboard</h2>
        <div className="stats-grid">
          <div className="stat-card">
            <span>Listings tracked</span>
            <strong>{listings.length}</strong>
          </div>
          <div className="stat-card">
            <span>Average score</span>
            <strong>{averageScore}</strong>
          </div>
        </div>

        <div className="listing-list">
          {listings.length === 0 ? (
            <p>No listings yet.</p>
          ) : (
            listings.map((listing, index) => (
              <article key={`${listing.title}-${index}`} className="listing-card">
                <div className="listing-header">
                  <h3>{listing.title}</h3>
                  <span className="score-pill">{listing.score}</span>
                </div>
                <p>Price: {listing.price ?? 'n/a'}</p>
                <p>Neighborhood: {listing.neighborhood ?? 'n/a'}</p>
                <p>Reasons: {listing.reasons?.join(', ') || 'n/a'}</p>
              </article>
            ))
          )}
        </div>
      </section>
    </main>
  );
}

export default App;
