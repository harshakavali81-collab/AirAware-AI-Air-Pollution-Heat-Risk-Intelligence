"""Regenerate original AirAware portfolio graphics from synthetic educational data.

Run from repository root: python -m scripts.make_gallery
Output PNG assets remain deliberately labeled SYNTHETIC / ILLUSTRATIVE.
"""
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT=Path(__file__).resolve().parents[1]
A=ROOT/'assets';A.mkdir(exist_ok=True)
D=pd.read_csv(ROOT/'data/processed/hyderabad_synthetic_pm25.csv',parse_dates=['date'])
C={'bg':'#071c27','panel':'#102e3b','line':'#33505d','text':'#eaf6f6','muted':'#a3baca','green':'#6beac2','blue':'#83b9fe','amber':'#fbc87c','rose':'#f88e9e'}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'figure.facecolor':C['bg'],'axes.facecolor':C['panel'],'axes.labelcolor':C['muted'],'xtick.color':C['muted'],'ytick.color':C['muted'],'text.color':C['text']})
def clean(ax):
    for s in ax.spines.values():s.set_visible(False)
    ax.grid(axis='y',alpha=.18,color=C['muted'])
def title(ax,t,sub):
    ax.set_title(t,color=C['text'],fontsize=20,loc='left',pad=34,fontweight='bold')
    ax.text(0,1.015,sub,transform=ax.transAxes,fontsize=10,color=C['amber'],va='bottom')
def save(fig,name):
    fig.savefig(A/name,dpi=136,bbox_inches='tight',pad_inches=.32,facecolor=fig.get_facecolor());plt.close(fig)

# 4 — distribution
fig,ax=plt.subplots(figsize=(11,5.6));ax.hist(D.pm25,bins=23,color=C['green'],alpha=.9,edgecolor=C['bg']);ax.axvline(D.pm25.mean(),color=C['amber'],ls='--',lw=2,label=f'Synthetic mean: {D.pm25.mean():.1f} µg/m³');clean(ax)
title(ax,'Distribution of demo PM2.5 measurements','SYNTHETIC DATA · NOT OBSERVED STATION READINGS');ax.set_xlabel('PM2.5 concentration (µg/m³)');ax.set_ylabel('Number of synthetic readings');ax.legend(frameon=False,labelcolor=C['text']);fig.tight_layout();save(fig,'pm25-distribution.png')
# 5 — weekly patterns
D['weekday']=D.date.dt.day_name();wd=D.groupby('weekday').pm25.agg(['mean','count']).reindex(['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']);fig,ax=plt.subplots(figsize=(11,5.6));bars=ax.bar(wd.index,wd['mean'],color=[C['green'] if i<5 else C['blue'] for i in range(7)]);clean(ax);title(ax,'Weekday pattern — synthetic demo','ILLUSTRATIVE ONLY · DOES NOT IDENTIFY REAL HUMAN EXPOSURE');ax.set_ylabel('Average PM2.5 (µg/m³)');ax.set_ylim(0,max(wd['mean'])*1.22)
for b in bars: ax.text(b.get_x()+b.get_width()/2,b.get_height()+.7,f'{b.get_height():.1f}',ha='center',color=C['text'],fontsize=10)
fig.tight_layout();save(fig,'weekly-seasonality.png')
# 7 — station and coverage reliability
stations=sorted(D.station.unique());days=D.date.nunique();count=D.groupby('station').date.nunique().reindex(stations);pct=(count/days*100)
fig,ax=plt.subplots(figsize=(11,5.2));ax.barh(stations,pct,color=[C['green'],C['blue'],C['amber']]);clean(ax);title(ax,'Reporting coverage by synthetic station','SYNTHETIC DEMO · COVERAGE IS SAMPLE COMPLETENESS ONLY');ax.set_xlabel('Days represented in sample (%)');ax.set_xlim(0,110)
for i,x in enumerate(pct):ax.text(min(x+1,103),i,f'{x:.0f}%',va='center',color=C['text'])
fig.tight_layout();save(fig,'data-coverage.png')

# box diagram helpers
from matplotlib.patches import ArrowStyle

def diagram_setup(heading,desc,figsize=(14,7)):
    fig,ax=plt.subplots(figsize=figsize);ax.set_xlim(0,14);ax.set_ylim(0,7);ax.axis('off');ax.set_facecolor(C['bg']);fig.patch.set_facecolor(C['bg']);ax.text(.4,6.68,heading,fontsize=24,fontweight='bold',color=C['text']);ax.text(.4,6.25,desc,fontsize=11,color=C['amber']);return fig,ax

def node(ax,x,y,w,h,name,sub,accent=None):
    accent=accent or C['green'];box=FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.08,rounding_size=.16',fc=C['panel'],ec=accent,lw=1.7);ax.add_patch(box)
    ax.text(x+.19,y+h*.64,name,fontsize=13,color=C['text'],fontweight='bold',va='center');ax.text(x+.19,y+h*.31,sub,fontsize=9,color=C['muted'],va='center');return x+w/2,y+h/2

def edge(ax,a,b):ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=18,linewidth=2,color=C['blue'],connectionstyle='arc3,rad=0'))
# 8 — architecture
fig,ax=diagram_setup('SYSTEM ARCHITECTURE','REAL-SOURCE CONNECTORS OPTIONAL · DEMO MODE IS EXPLICIT')
node(ax,.5,4.65,3,1.1,'OpenAQ v3','Sensor readings / API key',C['blue']);node(ax,.5,2.85,3,1.1,'Open-Meteo','Grid-model weather fields',C['blue']);node(ax,.5,1.1,3,1.1,'Synthetic mode','Clearly labeled seeded data',C['amber']);node(ax,4.65,2.85,3.25,2,'Ingestion + QA','UTC · units · missingness · provenance');node(ax,9,4.3,4.2,1.35,'FastAPI + SQLite','Read-only endpoints · city views');node(ax,9,1.85,4.2,1.35,'React dashboard','Maps · trends · quality · forecast')
for y in [5.2,3.4,1.65]:edge(ax,(3.63,y),(4.56,3.85));edge(ax,(7.98,3.95),(8.9,4.85));edge(ax,(11.1,4.18),(11.1,3.28));ax.text(4.65,.55,'Model training is offline; API forecast stays a separately labeled persistence baseline.',color=C['amber'],fontsize=10);save(fig,'system-architecture.png')
# 9 — data pipeline
fig,ax=diagram_setup('DATA ENGINEERING PIPELINE','PROVENANCE PRESERVED THROUGH EVERY TRANSFORMATION')
items=[('01  Collect','OpenAQ / demo'),('02  Validate','Units + schema'),('03  Normalize','UTC + PM2.5'),('04  Aggregate','Station / day'),('05  Persist','SQLite / CSV')]
for i,(h,d) in enumerate(items):
    x=.5+i*2.75;node(ax,x,3.2,2.3,1.5,h,d,[C['blue'],C['green'],C['amber'],C['blue'],C['green']][i]);
    if i:edge(ax,(x-.39,3.95),(x-.09,3.95))
ax.text(.6,2.2,'Quality gates: retain source · reject unsupported units · disclose missing data · check freshness',fontsize=12,color=C['text']);ax.text(.6,1.55,'Live-mode provider errors are surfaced. Synthetic fallback is NOT silently substituted.',fontsize=11,color=C['amber']);save(fig,'data-pipeline.png')
# 10 — full project workflow
fig,ax=diagram_setup('END-TO-END PROJECT WORKFLOW','REPRODUCIBLE INPUT → INSIGHT → VALIDATION → DEMONSTRATION')
node(ax,.6,4.2,3.4,1.4,'Ingest + inspect','OpenAQ · weather · synthetic');node(ax,5.2,4.2,3.4,1.4,'Transform + explore','Pandas · SQL · notebooks');node(ax,10,4.2,3.4,1.4,'Evaluate ML','Chronological train / test');node(ax,10,1.5,3.4,1.4,'Test + ship','Pytest · CI · Docker');node(ax,5.2,1.5,3.4,1.4,'Serve + visualize','FastAPI · React · Power BI CSV');node(ax,.6,1.5,3.4,1.4,'Communicate','README · model/data cards')
for a,b in [((4.11,4.9),(5.08,4.9)),((8.72,4.9),(9.88,4.9)),((11.7,4.1),(11.7,3.02)),((9.9,2.2),(8.72,2.2)),((5.1,2.2),(4.12,2.2))]:edge(ax,a,b)
ax.text(.55,.6,'Not a production air-quality alert or medical advice system · forecast ≠ observation',color=C['amber'],fontsize=11);save(fig,'project-workflow.png')
# 11 — source tree diagram (number kept 10 total with the 3 existing charts)
fig,ax=diagram_setup('SOURCE CODE MAP','TOP-LEVEL TREE · IMPLEMENTED PATHS AND RESPONSIBILITIES')
groups=[(.6,4.5,'backend/','FastAPI endpoints + SQLite'),(5.2,4.5,'src/airaware/','ingest · validate · forecast'),(9.8,4.5,'frontend/','React · charts · Leaflet'),(.6,2.3,'notebooks/','EDA · weather join · model eval'),(5.2,2.3,'tests/ + scripts/','27 tests · exports · gallery'),(9.8,2.3,'docs/ + powerbi/','architecture · guides · DAX')]
for i,(x,y,name,subtitle) in enumerate(groups):node(ax,x,y,3.75,1.28,name,subtitle,[C['green'],C['blue'],C['amber']][i%3]);
ax.text(.7,1.45,'Root: README.md · .env.example · pyproject.toml · Dockerfile · docker-compose.yml · .github/workflows/ci.yml',fontsize=11,color=C['text'])
ax.text(.7,.86,'Illustrative architecture tree, not an auto-generated filesystem inventory. See docs/PROJECT_STRUCTURE.md for exact paths.',fontsize=10,color=C['amber'])
save(fig,'project-tree.png')
print('Gallery:',sorted(p.name for p in A.glob('*.png')))
