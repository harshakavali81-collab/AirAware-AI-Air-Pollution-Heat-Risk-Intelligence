"""Write executable notebooks that use this package and synthetic data."""
from pathlib import Path
import nbformat as nbf
ROOT=Path(__file__).resolve().parents[1]
BOOKS=ROOT/'notebooks';BOOKS.mkdir(exist_ok=True)
def save(name, title, blocks):
    book=nbf.v4.new_notebook()
    book.cells=[nbf.v4.new_markdown_cell(f'# {title}\n\n**SYNTHETIC DEMONSTRATION DATA — NOT REAL CITY MEASUREMENTS.**')]
    for text in blocks: book.cells.append(nbf.v4.new_code_cell(text))
    book.metadata={'kernelspec': {'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python'}}
    nbf.write(book,BOOKS/name)
save('01_air_quality_eda.ipynb','01 · PM2.5 exploratory analysis',[
    'from src.airaware.ingestion.demo import demo_readings\nfrom src.airaware.processing.validation import validate_measurements, coverage\nimport matplotlib.pyplot as plt',
    "raw=demo_readings('Hyderabad',120)\ndf=validate_measurements(raw)\nprint(coverage(df,120))\ndf.head()",
    "daily=df.groupby('date',as_index=False).pm25.mean()\nax=daily.plot(x='date',y='pm25',title='SYNTHETIC PM2.5 daily city mean',figsize=(11,4))\nax.set_ylabel('µg/m³'); plt.show()",
    "df.groupby('station').pm25.agg(['mean','std','min','max','count']).round(2)"])
save('02_weather_join.ipynb','02 · Weather join (source-separation example)',[
    'from src.airaware.ingestion.demo import demo_readings\nfrom src.airaware.processing.features import daily_city_average,join_weather\nimport pandas as pd',
    "pm=daily_city_average(demo_readings('Hyderabad',30))",
    "weather=pd.DataFrame({'date':pd.to_datetime(pm.date).dt.date.astype(str),'temperature_c':[29+i%8 for i in range(len(pm))]})\n# Generated *example weather*, not fetched from a weather service.\njoined=join_weather(pm,weather)\njoined.tail()",
    "print('Missing values:',joined.isna().sum().to_dict())"])
save('03_forecast_evaluation.ipynb','03 · Chronological forecast evaluation',[
    'from src.airaware.models.train import train_and_evaluate\nimport pandas as pd\nimport matplotlib.pyplot as plt',
    "report=train_and_evaluate('Hyderabad')\nreport",
    "scores=pd.DataFrame({'Persistence':report['baseline'],'Random Forest':report['random_forest']})\nscores.plot(kind='bar',title='SYNTHETIC holdout error: lower is better',rot=0);plt.ylabel('µg/m³');plt.show()",
    "print('Only on synthetic data; cannot claim verified real-world forecast accuracy.')"])
print('Wrote notebooks')
