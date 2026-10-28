import React from 'react';
export default function Metric({label, value, unit, detail, icon: Icon, accent='mint'}) {
  return <article className="metric panel"><div className="metric-top"><span>{label}</span>{Icon&&<Icon className={'metric-icon '+accent} size={18}/>}</div>
    <div className="metric-value">{value ?? '—'}{value != null && unit && <small>{unit}</small>}</div><div className="metric-detail">{detail}</div></article>;
}
