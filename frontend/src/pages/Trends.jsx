import React from 'react';
import TrendChart from '../components/TrendChart.jsx';
export default function Trends({data}) {
  const rows=data.trends?.trends||[]; const avg=rows.length?rows.reduce((a,r)=>a+r.pm25,0)/rows.length:null;
  return <section className="panel chart-panel"><div className="section-heading"><div><span className="eyebrow">TEMPORAL ANALYSIS</span><h2>Daily PM2.5 trends</h2></div><span className="soft-badge">{rows.length} days</span></div>
    <div className="analytic-summary"><div><span>Period mean</span><strong>{avg==null?'—':avg.toFixed(1)} <small>µg/m³</small></strong></div><div><span>Observation type</span><strong>{data.overview.mode==='demo'?'Synthetic':'Aggregated measurements'}</strong></div></div>
    <TrendChart rows={rows} height={340}/><p className="small-note">Mean values are computed only from stations that reported on each date. Changing reporting stations can alter the aggregated signal.</p></section>;
}
