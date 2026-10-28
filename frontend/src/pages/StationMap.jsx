import React from 'react';
import {MapContainer, TileLayer, CircleMarker, Popup} from 'react-leaflet';
export default function StationMap({data}) {
  const o=data.overview; const stations=(data.stations?.stations||[]).filter(s=>s.latitude!=null&&s.longitude!=null);
  return <section className="panel"><div className="section-heading"><div><span className="eyebrow">GEO-SPATIAL VIEW</span><h2>Station explorer</h2></div><span className="soft-badge">{stations.length} points</span></div>
    <p className="subtle">Points show monitoring locations only in live mode. In demo mode all markers are fictitious and are not actual sensors.</p>
    <div className="map-area"><MapContainer key={o.city} center={[o.latitude,o.longitude]} zoom={10} style={{height:'100%',width:'100%'}} scrollWheelZoom={false}>
      <TileLayer attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors' url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"/>
      {stations.map(s=><CircleMarker key={s.id} center={[s.latitude,s.longitude]} radius={11} pathOptions={{color:'#093529',fillColor:'#37dfac',fillOpacity:.85,weight:3}}><Popup><b>{s.name}</b><p>{s.pm25 ?? '—'} µg/m³ PM2.5 · daily mean</p><small>{s.last_day || 'No observations'} · {s.source}</small></Popup></CircleMarker>)}
    </MapContainer></div>
    <p className="small-note">Map background © OpenStreetMap contributors. OpenAQ stations are irregularly distributed; blank areas do not imply clean air.</p>
  </section>;
}
