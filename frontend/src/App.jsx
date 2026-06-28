import { useEffect, useState } from 'react';

const API_BASE = 'http://localhost:8000/api';

const emptyForm = {
  brand: '',
  model: '',
  year: '',
  hours: '',
  purchasePrice: '',
  location: '',
  transportCost: '',
  repairCost: '',
  estimatedResaleValue: '',
  notes: ''
};

function App() {
  const [formData, setFormData] = useState(emptyForm);
  const [listings, setListings] = useState([]);
  const [status, setStatus] = useState('Analyze a deal to see its projected ROI.');
  const [analysis, setAnalysis] = useState(null);

  async function loadListings() {
    try {
      const response = await fetch(`${API_BASE}/listings`);
      const data = await response.json();
      setListings(data);
      setStatus(data.length ? `Loaded ${data.length} equipment opportunities.` : 'No equipment opportunities yet.');
    } catch (error) {
      setStatus('Unable to reach the backend service.');
      console.error(error);
    }
  }

  useEffect(() => {
    loadListings();
  }, []);

  function handleFieldChange(event) {
    const { name, value } = event.target;
    setFormData((previous) => ({ ...previous, [name]: value }));
  }

  async function handleAnalyzeDeal(event) {
    event.preventDefault();
    setStatus('Analyzing deal...');

    const row = [
      formData.brand,
      formData.model,
      formData.year,
      formData.hours,
      formData.purchasePrice,
      formData.location,
      formData.transportCost,
      formData.repairCost,
      formData.estimatedResaleValue,
      formData.notes
    ].join('|');

    try {
      const response = await fetch(`${API_BASE}/listings/import`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ rows: [row] })
      });
      const result = await response.json();

      if (response.ok) {
        const latestListing = result.listings?.at(-1) || null;
        setAnalysis(latestListing);
        setFormData(emptyForm);
        setStatus(`Analyzed ${result.imported} equipment opportunity(ies).`);
        await loadListings();
      } else {
        setAnalysis(null);
        setStatus(result.detail || 'Analysis failed.');
      }
    } catch (error) {
      setAnalysis(null);
      setStatus('Analysis failed.');
      console.error(error);
    }
  }

  async function handleClear() {
    await fetch(`${API_BASE}/listings`, { method: 'DELETE' });
    await loadListings();
    setAnalysis(null);
    setStatus('Cleared.');
  }

  async function handleExportCsv() {
    try {
      const response = await fetch(`${API_BASE}/listings/export.csv`);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'equipment_deals.csv';
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      setStatus('Exported CSV.');
    } catch (error) {
      setStatus('CSV export failed.');
      console.error(error);
    }
  }

  const averageScore = listings.length
    ? (listings.reduce((sum, item) => sum + (item.roi_percent || 0), 0) / listings.length).toFixed(1)
    : '0.0';

  return (
    <main>
      <section className="card hero">
        <h1>RowKey OS / Project Titan</h1>
        <p>Phase 1 MVP for manual heavy equipment import, ROI scoring, and a simple decision dashboard.</p>
      </section>

      <section className="card">
        <h2>Equipment deal form</h2>
        <form onSubmit={handleAnalyzeDeal} className="deal-form">
          <div className="form-grid">
            <label>
              Brand
              <input name="brand" value={formData.brand} onChange={handleFieldChange} placeholder="CAT" />
            </label>
            <label>
              Model
              <input name="model" value={formData.model} onChange={handleFieldChange} placeholder="320D" />
            </label>
            <label>
              Year
              <input name="year" type="number" value={formData.year} onChange={handleFieldChange} placeholder="2018" />
            </label>
            <label>
              Hours
              <input name="hours" type="number" value={formData.hours} onChange={handleFieldChange} placeholder="6200" />
            </label>
            <label>
              Purchase Price
              <input name="purchasePrice" type="number" value={formData.purchasePrice} onChange={handleFieldChange} placeholder="125000" />
            </label>
            <label>
              Location
              <input name="location" value={formData.location} onChange={handleFieldChange} placeholder="Denver" />
            </label>
            <label>
              Transport Cost
              <input name="transportCost" type="number" value={formData.transportCost} onChange={handleFieldChange} placeholder="3500" />
            </label>
            <label>
              Repair Cost
              <input name="repairCost" type="number" value={formData.repairCost} onChange={handleFieldChange} placeholder="4500" />
            </label>
            <label>
              Estimated Resale Value
              <input name="estimatedResaleValue" type="number" value={formData.estimatedResaleValue} onChange={handleFieldChange} placeholder="145000" />
            </label>
            <label className="full-width">
              Notes
              <textarea name="notes" value={formData.notes} onChange={handleFieldChange} placeholder="Serviced and ready to work" />
            </label>
          </div>

          <div className="actions">
            <button type="submit">Analyze Deal</button>
            <button type="button" className="secondary" onClick={handleClear}>Clear</button>
            <button type="button" onClick={handleExportCsv}>Export CSV</button>
          </div>
        </form>
        <p className="status">{status}</p>

        {analysis ? (
          <div className="analysis-summary">
            <h3>Latest deal summary</h3>
            <div className="stats-grid">
              <div className="stat-card">
                <span>Total cost</span>
                <strong>${analysis.total_cost?.toLocaleString() ?? 'n/a'}</strong>
              </div>
              <div className="stat-card">
                <span>Expected profit</span>
                <strong>${analysis.expected_profit?.toLocaleString() ?? 'n/a'}</strong>
              </div>
              <div className="stat-card">
                <span>ROI</span>
                <strong>{analysis.roi_percent ?? 'n/a'}%</strong>
              </div>
              <div className="stat-card">
                <span>Recommendation</span>
                <strong>{analysis.recommendation || 'n/a'}</strong>
              </div>
            </div>
          </div>
        ) : null}
      </section>

      <section className="card">
        <h2>Dashboard</h2>
        <div className="stats-grid">
          <div className="stat-card">
            <span>Equipment tracked</span>
            <strong>{listings.length}</strong>
          </div>
          <div className="stat-card">
            <span>Average ROI</span>
            <strong>{averageScore}%</strong>
          </div>
        </div>

        <div className="listing-list">
          {listings.length === 0 ? (
            <p>No equipment opportunities yet.</p>
          ) : (
            listings.map((listing, index) => (
              <article key={`${listing.title}-${index}`} className="listing-card">
                <div className="listing-header">
                  <h3>{listing.title}</h3>
                  <span className="score-pill">{listing.recommendation}</span>
                </div>
                <p>{listing.brand} {listing.model} • {listing.year} • {listing.hours} hrs</p>
                <p>Price: ${listing.price?.toLocaleString() ?? 'n/a'}</p>
                <p>Overall Score: {listing.overall_score ?? 'n/a'}/10</p>
                <p>Profit Potential: {listing.profit_potential ?? 'n/a'}/10</p>
                <p>Risk: {listing.risk ?? 'n/a'}/10</p>
                <p>Repair Difficulty: {listing.repair_difficulty ?? 'n/a'}/10</p>
                <p>Ease of Transport: {listing.ease_of_transport ?? 'n/a'}/10</p>
                <p>Expected Days to Sell: {listing.expected_days_to_sell ?? 'n/a'}</p>
                <p>ROI: {listing.roi_percent ?? 'n/a'}%</p>
                <p>Expected profit: ${listing.expected_profit?.toLocaleString() ?? 'n/a'}</p>
                <p>Location: {listing.location ?? 'n/a'}</p>
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
