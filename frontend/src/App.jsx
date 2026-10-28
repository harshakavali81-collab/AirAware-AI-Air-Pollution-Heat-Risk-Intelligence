import React, {useEffect,useState} from 'react';
import {Activity, LayoutDashboard, MapPinned, ChartNoAxesCombined, CalendarClock, ShieldCheck, Github, ArrowUpRight, CloudSun, Leaf, Menu, X} from 'lucide-react';
import {query} from './api/client.js';
import Dashboard from './pages/Dashboard.jsx';
import StationMap from './pages/StationMap.jsx';
import Forecast from './pages/Forecast.jsx';
import Trends from './pages/Trends.jsx';
import Quality from './pages/Quality.jsx';
const cities=['Hyderabad','Delhi','Mumbai','Bengaluru','Chennai'];
const tabs=[['Dashboard',LayoutDashboard],['Station map',MapPinned],['Forecast',CalendarClock],['Trends',ChartNoAxesCombined],['Data quality',ShieldCheck]];
function App(){
  const [city,setCity]=useState('Hyderabad'); const [tab,setTab]=useState('Dashboard'); const [data,setData]=useState(null);
  const [error,setError]=useState(''); const [loading,setLoading]=useState(true); const [menu,setMenu]=useState(false);
  useEffect(()=>{const abort=new AbortController();setLoading(true);setError('');
    Promise.all(['overview','stations','trends','forecast','quality'].map(n=>query(n,city,n==='trends'?'days=30':'',abort.signal).then(v=>[n,v])))
      .then(res=>{if(!abort.signal.aborted) setData(Object.fromEntries(res));})
      .catch(err=>{if(!abort.signal.aborted){setData(null);setError(err.message);}})
      .finally(()=>{if(!abort.signal.aborted) setLoading(false);});
    return ()=>abort.abort();},[city]);
  const screen={Dashboard, 'Station map':StationMap,Forecast,Trends,'Data quality':Quality}[tab];
  return <div className="app-shell">
    <aside className={'sidebar '+(menu?'mobile-open':'')}><div className="brand"><span className="brand-mark"><Leaf size={22}/></span><div>AirAware<span>AI</span><small>ENVIRONMENTAL INTELLIGENCE</small></div></div>
      <div className="side-label">WORKSPACE</div><nav aria-label="Main navigation">{tabs.map(([name,Icon])=><button type="button" key={name} className={'nav-option '+(tab===name?'active':'')} onClick={()=>{setTab(name);setMenu(false);}}><Icon size={18}/>{name}{tab===name&&<span className="nav-pip"/>}</button>)}</nav>
      <div className="sidebar-bottom"><div className="online-pill"><i/>API connection required</div><p>Explore the air. Understand the data.</p><a href="https://docs.openaq.org" target="_blank" rel="noreferrer">About OpenAQ <ArrowUpRight size={14}/></a></div>
    </aside>
    <div className="main-view"><header className="topbar"><button type="button" className="mobile-menu" aria-label="Toggle menu" onClick={()=>setMenu(!menu)}>{menu?<X size={23}/>:<Menu size={23}/>}</button><div className="breadcrumb">PLATFORM <span>/</span> {tab.toUpperCase()}</div><div className="top-actions"><span className="system-tag"><Activity size={14}/> SOURCE-AWARE</span><label className="city-select"><MapPinned size={16}/><select value={city} aria-label="Select city" onChange={e=>setCity(e.target.value)}>{cities.map(c=><option key={c}>{c}</option>)}</select></label></div></header>
      <main className="main-content"><div className="hero"><div><div className="eyebrow">THE ENVIRONMENT, DECODED <span className="hero-dot"/></div><h1>{tab==='Dashboard'?'Breathe informed.':tab+'.'}<br/><em>Understand your atmosphere.</em></h1><p>Discover pollution patterns, weather context and station data with transparent uncertainty.</p></div><div className="hero-decoration"><CloudSun size={72} strokeWidth={1.15}/></div></div>
      {data && <div className={'source-banner '+(data.overview.mode==='demo'?'demo':'live')} role="status"><strong>{data.overview.mode==='demo'?'DEMO MODE · SYNTHETIC DATA':'LIVE SOURCE · OPENAQ'}</strong><span>{data.overview.notice}</span></div>}
      {loading?<div className="loading panel">Loading environmental data…</div>:error?<div role="alert" className="error panel"><b>Data unavailable</b><p>{error}</p><p>For local demo mode, set AIR_DATA_MODE=demo. Live mode requires valid OpenAQ credentials and reporting stations.</p></div>:data?<div className="page-body"><>{React.createElement(screen,{data})}</></div>:null}
      <footer className="main-footer"><span>AirAware AI · Public-interest environmental analytics</span><span>Informational only · Not medical or official emergency advice</span></footer></main>
    </div>
  </div>;
}
export default App;
