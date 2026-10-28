import React from 'react';
import {ResponsiveContainer, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip} from 'recharts';
export default function TrendChart({rows=[], forecast=[], height=270}) {
  const entries=[...rows.map(x=>({...x, forecast:null})),...forecast.map(x=>({date:x.date, pm25:null, forecast:x.pm25}))];
  if (!entries.length) return <div className="empty">No series available for this city and date range.</div>;
  return <div style={{width:'100%',height}} role="img" aria-label="PM2.5 daily series and separate forecast baseline">
    <ResponsiveContainer><AreaChart data={entries} margin={{top:15,right:15,bottom:0,left:-18}}>
      <defs><linearGradient id="chartFill" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#3ce1b0" stopOpacity={.35}/><stop offset="95%" stopColor="#3ce1b0" stopOpacity={0}/></linearGradient></defs>
      <CartesianGrid stroke="#29414b" vertical={false} strokeDasharray="3 6"/>
      <XAxis dataKey="date" tick={{fill:'#91a8b2',fontSize:11}} tickFormatter={t=>t.slice(5)} minTickGap={28} axisLine={false} tickLine={false}/>
      <YAxis tick={{fill:'#91a8b2',fontSize:11}} axisLine={false} tickLine={false}/>
      <Tooltip contentStyle={{background:'#102b34',border:'1px solid #32505b',borderRadius:12,color:'#f2ffff'}} formatter={(v,n)=>[`${Number(v).toFixed(1)} µg/m³`,n==='pm25'?'Historical daily mean':'Baseline forecast']}/>
      <Area type="monotone" dataKey="pm25" stroke="#3ce1b0" strokeWidth={3} fill="url(#chartFill)" connectNulls={false} dot={false} name="pm25"/>
      <Area type="monotone" dataKey="forecast" stroke="#f9bf6e" strokeDasharray="6 4" strokeWidth={3} fill="none" name="forecast" dot={false}/>
    </AreaChart></ResponsiveContainer></div>;
}
