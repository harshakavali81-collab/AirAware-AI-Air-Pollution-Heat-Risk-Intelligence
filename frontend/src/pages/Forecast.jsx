import React from 'react';
import {TriangleAlert} from 'lucide-react';
import TrendChart from '../components/TrendChart.jsx';
export default function Forecast({data}) {
  const f=data.forecast;
  return <div className="two-column"><section className="panel chart-panel"><div className="section-heading"><div><span className="eyebrow">EXPERIMENTAL PROJECTION</span><h2>Seven-day baseline</h2></div></div>
    <div className="legend"><span><i className="dot mint"/>Historical</span><span><i className="dot amber"/>Projected (not measured)</span></div>
    <TrendChart rows={(data.trends?.trends||[]).slice(-14)} forecast={f?.forecast||[]}/>
    <p className="small-note">Historical daily mean is a city-level aggregate over available reporting stations. The dashed line is a persistence baseline only.</p></section>
    <section className="panel"><div className="section-heading"><div><span className="eyebrow">MODEL CARD</span><h2>How the forecast works</h2></div></div>
      <div className="model-box">Last observed day → future daily baseline</div><p className="subtle">No model is automatically trained or calibrated when the API starts. Run the documented offline training script to compare a lag-feature Random Forest against this baseline on a chronological holdout.</p>
      <div className="callout"><TriangleAlert size={22}/><p><b>Not an official forecast.</b> The projection is not an emergency warning and must not be interpreted as an observed value or verified prediction.</p></div>
    </section></div>;
}
