# Power BI import-ready example

1. In the project root run `python -m scripts.export_demo`.
2. In Power BI Desktop: **Get Data → Text/CSV → `data/processed/hyderabad_synthetic_pm25.csv`**.
3. Change `date` to Date and `pm25` to Decimal number. Add a Date table and link by date.
4. Make line charts by Date, station bars, map only when real station coordinates exist, and a data-quality page.
5. Add a **Synthetic data** banner to every report page. Replace the CSV only after obtaining real source data and checking licenses, units and source timestamps.

Example DAX (rename your table to `Readings`):

```dax
Average PM25 = AVERAGE(Readings[pm25])
Reporting Stations = DISTINCTCOUNT(Readings[station])
Observed Station Days = COUNTROWS(SUMMARIZE(Readings, Readings[date], Readings[station]))
```

A `.pbix` binary report is not included: it must be authored and validated using Microsoft Power BI Desktop. The CSV and measures are the reproducible handoff.
