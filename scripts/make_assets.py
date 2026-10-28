"""Generate original charts from synthetic examples. All previews are labeled demo."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from src.airaware.ingestion.demo import demo_readings
from src.airaware.processing.features import daily_city_average
from src.airaware.models.train import train_and_evaluate

ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'assets'
ASSETS.mkdir(exist_ok=True)
RAW=demo_readings('Hyderabad',90)
D=daily_city_average(RAW)
y=D.pm25.to_numpy(); xs=np.arange(len(D))
plt.rcParams.update({'font.family':'DejaVu Sans','text.color':'#e6f6f2','axes.labelcolor':'#96b5b9','xtick.color':'#8aafb6','ytick.color':'#8aafb6','font.size':11})
fig=plt.figure(figsize=(14,8),facecolor='#0a1d27')
fig.text(.06,.92,'AIR AWARE',color='#58edbd',weight='bold',fontsize=16)
fig.text(.24,.92,'/   ENVIRONMENTAL INTELLIGENCE',color='#8da8b4',fontsize=10)
fig.text(.06,.84,'Air quality, made understandable.',fontsize=28,weight='bold')
fig.text(.06,.78,'ILLUSTRATIVE PREVIEW  •  SYNTHETIC DATA  •  NOT A LIVE DASHBOARD SCREENSHOT',color='#e7b570',fontsize=9)
for i,(title,val,unit) in enumerate([('DAILY MEAN PM2.5',f'{y[-1]:.1f}','µg/m³'),('REPORTING POINTS','03','synthetic sites'),('PERIOD','90','days')]):
    x=.06+i*.31
    rect=FancyBboxPatch((x,.6),.275,.125,boxstyle='round,pad=0.012,rounding_size=0.015',transform=fig.transFigure,facecolor='#15323d',edgecolor='#2b5861')
    fig.add_artist(rect)
    fig.text(x+.024,.683,title,color='#9ab6bb',fontsize=9,weight='bold')
    fig.text(x+.024,.625,val,color='#64e9bb',fontsize=26,weight='bold')
    fig.text(x+.16,.633,unit,color='#9ab6bb',fontsize=10)
ax=fig.add_axes([.06,.13,.89,.40],facecolor='#102b35')
ax.plot(xs,y,color='#5be9ba',linewidth=2.7)
ax.fill_between(xs,y,0,color='#5be9ba',alpha=.13)
ax.grid(axis='y',color='#2d4c54',linestyle='--',alpha=.6)
for s in ax.spines.values(): s.set_visible(False)
ax.set_xlim(0,len(y)-1);ax.set_ylim(0,max(y)*1.15)
ax.set_title('Daily PM2.5 concentration · synthetic Hyderabad example',loc='left',pad=18,color='#e8f6f3',weight='bold')
ax.set_ylabel('PM2.5 (µg/m³)')
ax.set_xticks([0,20,40,60,80]);ax.set_xticklabels([D.date.iloc[min(i,len(D)-1)].strftime('%b %d') for i in [0,20,40,60,80]])
fig.text(.06,.056,'Educational synthetic series; not evidence of actual air quality or public safety.',color='#8ba7b1',fontsize=9)
fig.savefig(ASSETS/'dashboard-preview.png',dpi=140,facecolor=fig.get_facecolor());plt.close(fig)

fig,ax=plt.subplots(figsize=(11,5),facecolor='#0a1d27');ax.set_facecolor('#102b35')
for name,color in [('DEMO-HYD-1','#5be9ba'),('DEMO-HYD-2','#f2bd6f'),('DEMO-HYD-3','#78aef4')]:
    s=RAW.loc[RAW.station==name].sort_values('date');ax.plot(s.date,s.pm25,label=name,color=color,linewidth=1.65,alpha=.9)
ax.set_title('PM2.5 by synthetic station · educational example',loc='left',color='white',fontsize=15,pad=20)
ax.set_ylabel('PM2.5 (µg/m³)');ax.grid(alpha=.15);ax.legend(frameon=False,labelcolor='#d9ece9',loc='upper right')
ax.tick_params(axis='x',rotation=45,labelsize=7);ax.xaxis.set_major_locator(plt.MaxNLocator(9))
for spine in ax.spines.values():spine.set_visible(False)
fig.tight_layout(pad=2);fig.savefig(ASSETS/'station-trends.png',dpi=130,facecolor=fig.get_facecolor());plt.close(fig)

r=train_and_evaluate('Hyderabad')
fig,ax=plt.subplots(figsize=(8,4.5),facecolor='#0a1d27');ax.set_facecolor('#102b35')
bar1=ax.bar([0,1],[r['baseline']['mae'],r['baseline']['rmse']],width=.34,color='#74adfa',label='Prior-day baseline')
bar2=ax.bar([.36,1.36],[r['random_forest']['mae'],r['random_forest']['rmse']],width=.34,color='#5be9ba',label='Random forest')
ax.set_xticks([.18,1.18],['MAE','RMSE']);ax.set_ylabel('Error (µg/m³)');ax.set_ylim(0,6)
ax.set_title('Time-based holdout · SYNTHETIC DATA ONLY',loc='left',color='#e8f6f3',pad=18)
ax.legend(frameon=False,labelcolor='#e6f6f2');ax.grid(axis='y',color='#34525a',alpha=.3)
for spine in ax.spines.values():spine.set_visible(False)
fig.tight_layout(pad=2);fig.savefig(ASSETS/'model-evaluation.png',dpi=140,facecolor=fig.get_facecolor());plt.close(fig)
print('Generated charts:',*(p.name for p in ASSETS.glob('*.png')))
