import React from 'react';
export default function Quality({data}) {
  const q=data.quality||{}; const c=q.coverage||{};
  return <section className="panel"><div className="section-heading"><div><span className="eyebrow">DATA RELIABILITY</span><h2>Quality & provenance</h2></div></div>
    <div className="quality-grid"><div className="quality-card"><span>Station-day coverage</span><strong>{c.coverage_pct ?? '—'}%</strong><p>{c.observed_station_days ?? 0} observed / {c.expected_station_days ?? 0} expected</p></div><div className="quality-card"><span>Missing station-days</span><strong>{c.missing_pct ?? '—'}%</strong><p>Within the fixed 120-day window</p></div><div className="quality-card"><span>Most recent station-day</span><strong className="smaller">{q.freshness?.latest_date?.slice(0,10) || '—'}</strong><p>{q.freshness?.status || 'unknown'}</p></div></div>
    <h3>Exploratory anomaly flags</h3><p className="subtle">Flags detect unusually high or low changes in a rolling series; they are not validated regulatory exceedances or health alerts.</p>
    {(q.exploratory_anomalies||[]).length ? <ul className="anomaly-list">{q.exploratory_anomalies.map((r,i)=><li key={i}>{String(r.date).slice(0,10)}: {r.pm25} µg/m³ (z={r.z_score})</li>)}</ul> : <div className="empty">No series points crossed the exploratory threshold.</div>}
    <p className="small-note">{q.caveat}</p></section>;
}
