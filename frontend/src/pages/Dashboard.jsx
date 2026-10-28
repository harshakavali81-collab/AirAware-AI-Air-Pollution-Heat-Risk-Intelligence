import React from 'react';
import {Wind, ThermometerSun, Waves, RadioTower, ArrowUpRight, ArrowDownRight, Layers3, Clock3} from 'lucide-react';
import Metric from '../components/Metric.jsx';
import TrendChart from '../components/TrendChart.jsx';
function n(v) { return v == null ? '—' : Number(v).toFixed(1); }
export default function Dashboard({data}) {
  const o=data.overview; const rows=data.trends?.trends || []; const stations=data.stations?.stations||[];
  const w=o.weather||{}; const delta=o.day_change_pct;
  return <>
    <section className="metric-grid">
      <Metric label="PM2.5 · latest daily mean" value={n(o.latest_daily_mean)} unit="µg/m³" detail="Across reporting stations · not live AQI" icon={Wind}/>
      <Metric label="Apparent temperature" value={n(w.apparent_temperature_c)} unit="°C" detail={w.illustrative_heat_band ? `${w.illustrative_heat_band} · heuristic heat band` : 'Weather context'} icon={ThermometerSun} accent="amber"/>
      <Metric label="Relative humidity" value={w.humidity_pct == null ? null : Math.round(w.humidity_pct)} unit="%" detail="Weather model estimate · separate source" icon={Waves} accent="blue"/>
      <Metric label="Stations in dataset" value={o.station_count} detail={`${o.quality?.coverage_pct ?? 0}% observed station-day coverage`} icon={RadioTower}/>
    </section>
    <div className="content-grid">
      <section className="panel chart-panel"><div className="section-heading"><div><span className="eyebrow">HISTORICAL SIGNAL</span><h2>Pollution over time</h2></div><span className="soft-badge">Last {rows.length} days</span></div>
        <div className="legend"><span><i className="dot mint"/>PM2.5 daily average</span><span>Values in µg/m³</span></div><TrendChart rows={rows}/></section>
      <section className="panel insights"><div className="section-heading"><div><span className="eyebrow">DAILY BRIEF</span><h2>Environmental snapshot</h2></div><Layers3 size={19} color="#71ddbf"/></div>
        <div className="insight-line"><div>Day-over-day mean PM2.5</div><strong className={delta>0?'amber':'mint'}>{delta==null?'—':<>{delta>0?<ArrowUpRight size={15}/>:<ArrowDownRight size={15}/>} {Math.abs(delta)}%</>}</strong></div>
        <div className="insight-line"><div>Weather temperature</div><strong>{n(w.temperature_c)} °C</strong></div>
        <div className="insight-line"><div>Heat exposure band</div><strong className="caps">{w.illustrative_heat_band || 'Unavailable'}</strong></div>
        <div className="insight-line"><div>Freshness</div><strong>{o.freshness?.status || 'unknown'}</strong></div>
        <div className="callout"><Clock3 size={18}/><p><b>Check the timestamps.</b> Daily pollutant values can lag behind weather data. This dashboard does not provide emergency alerts or medical guidance.</p></div></section>
    </div>
    <section className="panel station-panel"><div className="section-heading"><div><span className="eyebrow">STATION COVERAGE</span><h2>Reading comparison</h2></div></div>
      <div className="station-grid">{stations.map(x=><div className="station-tile" key={x.id}><span className="station-dot"/><div><b>{x.name}</b><p>{x.id} · {x.last_day || 'No data'}</p></div><strong>{x.pm25 ?? '—'}<small> µg/m³</small></strong></div>)}</div>
    </section>
  </>;
}
