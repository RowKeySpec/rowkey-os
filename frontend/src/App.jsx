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
  comparableLowValue: '',
  comparableAverageValue: '',
  comparableHighValue: '',
  desiredMinimumRoi: '',
  notes: ''
};

const emptyListingDescription = '';

function toNumber(value) {
  const numericValue = Number(value);
  return Number.isFinite(numericValue) ? numericValue : 0;
}

function normalizeListing(listing = {}) {
  const purchasePrice = toNumber(listing.price ?? listing.purchase_price ?? 0);
  const transportCost = toNumber(listing.estimated_transport_cost ?? listing.transport_cost ?? 0);
  const repairCost = toNumber(listing.estimated_repair_cost ?? listing.repair_cost ?? 0);
  const estimatedResale = toNumber(listing.estimated_resale_value ?? listing.estimated_resale ?? 0);
  const totalInvestment = toNumber(listing.total_investment ?? purchasePrice + transportCost + repairCost);
  const estimatedGrossProfit = toNumber(listing.estimated_gross_profit ?? estimatedResale - purchasePrice);
  const netProfit = toNumber(listing.net_profit ?? estimatedResale - totalInvestment);
  const roiPercent = toNumber(
    listing.roi_percent ?? listing.roi ?? (totalInvestment > 0 ? (netProfit / totalInvestment) * 100 : 0)
  );
  const interestCost = toNumber(listing.interest_cost ?? 0);
  const annualizedRoi = toNumber(listing.annualized_roi ?? roiPercent);
  const expectedDaysToSell = Number.isFinite(Number(listing.expected_days_to_sell))
    ? Number(listing.expected_days_to_sell)
    : (roiPercent >= 25 ? 20 : roiPercent >= 15 ? 30 : 45);
  const recommendedMaxOffer = toNumber(listing.recommended_max_offer ?? Math.max(0, estimatedResale - repairCost - transportCost));
  const overallScore = listing.overall_score ?? listing.overallScore ?? null;
  const profitPotential = listing.profit_potential ?? listing.profitPotential ?? null;
  const risk = listing.risk ?? null;
  const repairDifficulty = listing.repair_difficulty ?? null;
  const easeOfTransport = listing.ease_of_transport ?? null;
  const recommendation = listing.recommendation ?? (roiPercent >= 25 ? 'BUY_NOW' : roiPercent >= 15 ? 'NEGOTIATE' : 'PASS');
  const marketValueLow = toNumber(
    listing.market_value_low ?? listing.comparable_low_value ?? listing.comparable_low ?? listing.estimated_resale_value ?? 0
  );
  const marketValueAverage = toNumber(
    listing.market_value_average ?? listing.comparable_average_value ?? listing.comparable_average ?? listing.estimated_resale_value ?? 0
  );
  const marketValueHigh = toNumber(
    listing.market_value_high ?? listing.comparable_high_value ?? listing.comparable_high ?? listing.estimated_resale_value ?? 0
  );
  const desiredMinRoi = toNumber(listing.desired_minimum_roi_percent ?? listing.desired_min_roi ?? 15);
  const targetOffer = toNumber(listing.target_offer ?? 0);
  const maxOffer = toNumber(listing.max_offer ?? 0);
  const walkAwayPrice = toNumber(listing.walk_away_price ?? 0);
  const resaleConfidence = listing.resale_confidence ?? 'Medium';
  const negotiationConfidence = listing.negotiation_confidence ?? 0;
  const reasons = Array.isArray(listing.reasons) && listing.reasons.length
    ? listing.reasons
    : [
        roiPercent >= 25 ? 'Strong resale upside' : roiPercent >= 15 ? 'Solid margin for negotiation' : 'Weak ROI profile',
        listing.hours && Number(listing.hours) < 5000 ? 'Low usage hours' : 'Moderate usage',
        transportCost <= 3000 ? 'Manageable transport cost' : 'Higher transport cost'
      ];

  return {
    ...listing,
    title: listing.title || `${listing.brand || ''} ${listing.model || ''}`.trim(),
    price: purchasePrice,
    purchase_price: purchasePrice,
    estimated_transport_cost: transportCost,
    transport_cost: transportCost,
    estimated_repair_cost: repairCost,
    repair_cost: repairCost,
    estimated_resale_value: estimatedResale,
    estimated_resale: estimatedResale,
    total_investment: totalInvestment,
    estimated_gross_profit: estimatedGrossProfit,
    net_profit: netProfit,
    roi_percent: roiPercent,
    interest_cost: interestCost,
    annualized_roi: annualizedRoi,
    expected_days_to_sell: expectedDaysToSell,
    recommended_max_offer: recommendedMaxOffer,
    overall_score: overallScore,
    profit_potential: profitPotential,
    risk,
    repair_difficulty: repairDifficulty,
    ease_of_transport: easeOfTransport,
    recommendation,
    market_value_low: marketValueLow,
    market_value_average: marketValueAverage,
    market_value_high: marketValueHigh,
    comparable_low_value: toNumber(listing.comparable_low_value ?? listing.comparable_low ?? 0),
    comparable_average_value: toNumber(listing.comparable_average_value ?? listing.comparable_average ?? 0),
    comparable_high_value: toNumber(listing.comparable_high_value ?? listing.comparable_high ?? 0),
    target_offer: targetOffer,
    max_offer: maxOffer,
    walk_away_price: walkAwayPrice,
    resale_confidence: resaleConfidence,
    negotiation_confidence: negotiationConfidence,
    desired_minimum_roi_percent: desiredMinRoi,
    desired_min_roi: desiredMinRoi,
    reasons,
  };
}

function App() {
  const [formData, setFormData] = useState(emptyForm);
  const [listingDescription, setListingDescription] = useState(emptyListingDescription);
  const [listings, setListings] = useState([]);
  const [status, setStatus] = useState('Analyze a deal to see its projected ROI.');
  const [analysis, setAnalysis] = useState(null);
  const [showManualForm, setShowManualForm] = useState(true);

  async function loadListings() {
    try {
      const response = await fetch(`${API_BASE}/listings`);
      const data = await response.json();
      const normalizedListings = Array.isArray(data) ? data.map(normalizeListing) : [];
      setListings(normalizedListings);
      setStatus(normalizedListings.length ? `Loaded ${normalizedListings.length} equipment opportunities.` : 'No equipment opportunities yet.');
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

  function handleListingDescriptionChange(event) {
    setListingDescription(event.target.value);
  }

  async function handleAutoFillFromListing(event) {
    event.preventDefault();
    if (!listingDescription.trim()) {
      setStatus('Paste a listing description first.');
      return;
    }

    setStatus('Parsing listing description...');
    try {
      const response = await fetch(`${API_BASE}/listings/parse`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ description: listingDescription })
      });
      const result = await response.json();

      if (response.ok && result.extracted) {
        const extracted = result.extracted;
        setFormData({
          ...emptyForm,
          brand: extracted.brand || '',
          model: extracted.model || '',
          year: extracted.year ?? '',
          hours: extracted.hours ?? '',
          purchasePrice: extracted.purchasePrice ?? '',
          comparableLowValue: extracted.comparableLowValue ?? '',
          comparableAverageValue: extracted.comparableAverageValue ?? '',
          comparableHighValue: extracted.comparableHighValue ?? '',
          desiredMinimumRoi: extracted.desiredMinimumRoiPercent ?? '',
          location: extracted.location || '',
          notes: extracted.notes || ''
        });
        setShowManualForm(true);
        setStatus('Auto-filled the form from the listing description.');
      } else {
        setStatus('Unable to extract listing details.');
      }
    } catch (error) {
      setStatus('Listing parsing failed.');
      console.error(error);
    }
  }

  async function handleAnalyzeDeal(event) {
    event.preventDefault();
    setStatus('Analyzing deal...');

    try {
      const response = await fetch(`${API_BASE}/listings/import`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          brand: formData.brand,
          model: formData.model,
          year: formData.year || null,
          hours: formData.hours || null,
          purchase_price: formData.purchasePrice || null,
          location: formData.location,
          transport_cost: formData.transportCost || null,
          repair_cost: formData.repairCost || null,
          estimated_resale_value: formData.estimatedResaleValue || null,
          comparable_low_value: formData.comparableLowValue || null,
          comparable_average_value: formData.comparableAverageValue || null,
          comparable_high_value: formData.comparableHighValue || null,
          desired_minimum_roi_percent: formData.desiredMinimumRoi || null,
          notes: formData.notes
        })
      });
      const result = await response.json();

      if (response.ok) {
        const latestListing = result.listings?.at(-1) || null;
        setAnalysis(latestListing ? normalizeListing(latestListing) : null);
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

  const normalizedListings = listings.map(normalizeListing);
  const normalizedAnalysis = analysis ? normalizeListing(analysis) : null;

  const averageScore = normalizedListings.length
    ? (normalizedListings.reduce((sum, item) => sum + (item.roi_percent || 0), 0) / normalizedListings.length).toFixed(1)
    : '0.0';

  return (
    <main>
      <section className="card hero">
        <h1>RowKey OS / Project Titan</h1>
        <p>Phase 1 MVP for manual heavy equipment import, ROI scoring, and a simple decision dashboard.</p>
      </section>

      <section className="card">
        <h2>AI Listing Import Assistant</h2>
        <p>Paste a full marketplace listing description and let the assistant extract the core equipment details before you analyze the deal.</p>
        <form onSubmit={handleAnalyzeDeal} className="deal-form">
          <label className="full-width">
            Listing Description
            <textarea
              name="listingDescription"
              value={listingDescription}
              onChange={handleListingDescriptionChange}
              placeholder="Paste the full Marketplace, Craigslist, MachineryTrader, or similar listing here..."
            />
          </label>

          <div className="actions">
            <button type="button" onClick={handleAutoFillFromListing}>Auto Fill from Listing</button>
            <button type="button" className="secondary" onClick={() => { setListingDescription(emptyListingDescription); setFormData(emptyForm); setStatus('Cleared the listing assistant inputs.'); }}>
              Clear Assistant
            </button>
          </div>

          <div className="form-toggle-row">
            <button type="button" className={showManualForm ? 'secondary' : ''} onClick={() => setShowManualForm(true)}>
              Manual Entry
            </button>
            <button type="button" className={!showManualForm ? 'secondary' : ''} onClick={() => setShowManualForm(false)}>
              Hide Manual Form
            </button>
          </div>

          {showManualForm ? (
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
            <label>
              Comparable Low Value
              <input name="comparableLowValue" type="number" value={formData.comparableLowValue} onChange={handleFieldChange} placeholder="140000" />
            </label>
            <label>
              Comparable Average Value
              <input name="comparableAverageValue" type="number" value={formData.comparableAverageValue} onChange={handleFieldChange} placeholder="150000" />
            </label>
            <label>
              Comparable High Value
              <input name="comparableHighValue" type="number" value={formData.comparableHighValue} onChange={handleFieldChange} placeholder="160000" />
            </label>
            <label>
              Desired Minimum ROI %
              <input name="desiredMinimumRoi" type="number" value={formData.desiredMinimumRoi} onChange={handleFieldChange} placeholder="15" />
            </label>
              <label className="full-width">
                Notes
                <textarea name="notes" value={formData.notes} onChange={handleFieldChange} placeholder="Serviced and ready to work" />
              </label>
            </div>
          ) : null}

          <div className="actions">
            <button type="submit">Analyze Deal</button>
            <button type="button" className="secondary" onClick={handleClear}>Clear</button>
            <button type="button" onClick={handleExportCsv}>Export CSV</button>
          </div>
        </form>
        <p className="status">{status}</p>

        {normalizedAnalysis ? (
          <div className="analysis-summary">
            <h3>Latest deal summary</h3>
            <div className="stats-grid">
              <div className="stat-card">
                <span>Total investment</span>
                <strong>${normalizedAnalysis.total_investment?.toLocaleString() ?? 'n/a'}</strong>
              </div>
              <div className="stat-card">
                <span>Net profit</span>
                <strong>${normalizedAnalysis.net_profit?.toLocaleString() ?? 'n/a'}</strong>
              </div>
              <div className="stat-card">
                <span>ROI</span>
                <strong>{normalizedAnalysis.roi_percent ?? 'n/a'}%</strong>
              </div>
              <div className="stat-card">
                <span>Recommendation</span>
                <strong>{normalizedAnalysis.recommendation || 'n/a'}</strong>
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
            <strong>{normalizedListings.length}</strong>
          </div>
          <div className="stat-card">
            <span>Average ROI</span>
            <strong>{averageScore}%</strong>
          </div>
        </div>

        <div className="listing-list">
          {normalizedListings.length === 0 ? (
            <p>No equipment opportunities yet.</p>
          ) : (
            normalizedListings.map((listing, index) => (
              <article key={`${listing.title}-${index}`} className="listing-card">
                <div className="listing-header">
                  <h3>{listing.title}</h3>
                  <span className="score-pill">{listing.recommendation}</span>
                </div>

                <div className="executive-summary">
                  <div className="summary-primary">
                    <span className="summary-label">Equipment</span>
                    <strong>{listing.title}</strong>
                    <span className="summary-meta">{listing.year ?? 'n/a'} • {listing.hours ?? 'n/a'} hrs • {listing.location ?? 'n/a'}</span>
                  </div>
                  <div className="summary-metrics">
                    <div className="summary-metric">
                      <span>Score</span>
                      <strong>{listing.overall_score ?? 'n/a'}/10</strong>
                    </div>
                    <div className="summary-metric">
                      <span>ROI</span>
                      <strong>{listing.roi_percent ?? 'n/a'}%</strong>
                    </div>
                    <div className="summary-metric">
                      <span>Net profit</span>
                      <strong>${listing.net_profit?.toLocaleString() ?? listing.expected_profit?.toLocaleString() ?? 'n/a'}</strong>
                    </div>
                    <div className="summary-metric">
                      <span>Max offer</span>
                      <strong>${listing.recommended_max_offer?.toLocaleString() ?? 'n/a'}</strong>
                    </div>
                    <div className="summary-metric">
                      <span>Days to sell</span>
                      <strong>{listing.expected_days_to_sell ?? 'n/a'}</strong>
                    </div>
                  </div>
                </div>

                <div className="card-section">
                  <h4>Main deal info</h4>
                  <div className="metric-grid">
                    <div className="metric">
                      <span>Total investment</span>
                      <strong>${listing.total_investment?.toLocaleString() ?? listing.total_cost?.toLocaleString() ?? 'n/a'}</strong>
                    </div>
                    <div className="metric">
                      <span>Purchase price</span>
                      <strong>${listing.price?.toLocaleString() ?? 'n/a'}</strong>
                    </div>
                    <div className="metric">
                      <span>Expected days to sell</span>
                      <strong>{listing.expected_days_to_sell ?? 'n/a'}</strong>
                    </div>
                  </div>
                </div>

                <div className="card-section">
                  <h4>Profit numbers</h4>
                  <div className="metric-grid">
                    <div className="metric">
                      <span>Estimated gross profit</span>
                      <strong>${listing.estimated_gross_profit?.toLocaleString() ?? 'n/a'}</strong>
                    </div>
                    <div className="metric">
                      <span>Net profit</span>
                      <strong>${listing.net_profit?.toLocaleString() ?? listing.expected_profit?.toLocaleString() ?? 'n/a'}</strong>
                    </div>
                    <div className="metric">
                      <span>ROI</span>
                      <strong>{listing.roi_percent ?? 'n/a'}%</strong>
                    </div>
                    <div className="metric">
                      <span>Interest cost</span>
                      <strong>${listing.interest_cost?.toLocaleString() ?? 'n/a'}</strong>
                    </div>
                    <div className="metric">
                      <span>Annualized ROI</span>
                      <strong>{listing.annualized_roi ?? 'n/a'}%</strong>
                    </div>
                    <div className="metric">
                      <span>Suggested max offer</span>
                      <strong>${listing.recommended_max_offer?.toLocaleString() ?? 'n/a'}</strong>
                    </div>
                  </div>
                </div>

                <div className="card-section">
                  <h4>Scores</h4>
                  <div className="metric-grid">
                    <div className="metric">
                      <span>Overall score</span>
                      <strong>{listing.overall_score ?? 'n/a'}/10</strong>
                    </div>
                    <div className="metric">
                      <span>Profit potential</span>
                      <strong>{listing.profit_potential ?? 'n/a'}/10</strong>
                    </div>
                    <div className="metric">
                      <span>Risk</span>
                      <strong>{listing.risk ?? 'n/a'}/10</strong>
                    </div>
                    <div className="metric">
                      <span>Repair difficulty</span>
                      <strong>{listing.repair_difficulty ?? 'n/a'}/10</strong>
                    </div>
                    <div className="metric">
                      <span>Ease of transport</span>
                      <strong>{listing.ease_of_transport ?? 'n/a'}/10</strong>
                    </div>
                  </div>
                </div>

                <div className="card-section">
                  <h4>Market Intelligence</h4>
                  <div className="metric-grid">
                    <div className="metric">
                      <span>Market low</span>
                      <strong>${listing.market_value_low?.toLocaleString() ?? 'n/a'}</strong>
                    </div>
                    <div className="metric">
                      <span>Market average</span>
                      <strong>${listing.market_value_average?.toLocaleString() ?? 'n/a'}</strong>
                    </div>
                    <div className="metric">
                      <span>Market high</span>
                      <strong>${listing.market_value_high?.toLocaleString() ?? 'n/a'}</strong>
                    </div>
                    <div className="metric">
                      <span>Target offer</span>
                      <strong>${listing.target_offer?.toLocaleString() ?? 'n/a'}</strong>
                    </div>
                    <div className="metric">
                      <span>Max offer</span>
                      <strong>${listing.max_offer?.toLocaleString() ?? 'n/a'}</strong>
                    </div>
                    <div className="metric">
                      <span>Walk-away price</span>
                      <strong>${listing.walk_away_price?.toLocaleString() ?? 'n/a'}</strong>
                    </div>
                    <div className="metric">
                      <span>Resale confidence</span>
                      <strong>{listing.resale_confidence || 'n/a'}</strong>
                    </div>
                    <div className="metric">
                      <span>Negotiation confidence</span>
                      <strong>{listing.negotiation_confidence ?? 'n/a'}%</strong>
                    </div>
                  </div>
                </div>

                <div className="card-section">
                  <h4>Recommendation</h4>
                  <div className="metric-grid">
                    <div className="metric">
                      <span>Recommendation</span>
                      <strong>{listing.recommendation || 'n/a'}</strong>
                    </div>
                    <div className="metric">
                      <span>Notes</span>
                      <strong>{listing.notes || 'n/a'}</strong>
                    </div>
                  </div>
                </div>

                <p className="status">Reasons: {listing.reasons?.join(', ') || 'n/a'}</p>
              </article>
            ))
          )}
        </div>
      </section>
    </main>
  );
}

export default App;
