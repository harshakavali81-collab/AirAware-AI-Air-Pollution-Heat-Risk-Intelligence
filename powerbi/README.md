# AirAware Power BI project — source-controlled `.pbip` / PBIR report

**New:** [`AirAwareReport/AirAware.pbip`](AirAwareReport/AirAware.pbip) is an editable Power BI Project source package, with a Power BI tabular model (`model.bim`), 2 report pages, and 5 visual definitions. This is **not** a `.pbix` export, and cannot be validated in the Power BI Desktop application in this environment. The JSON files pass local structural checks; Power BI Desktop must validate/refresh and save the actual report.

## Open with Power BI Desktop (Windows)
1. Open `AirAwareReport/AirAware.pbip` using current Power BI Desktop with PBIP/PBIR support. It contains 90 **synthetic example observations embedded in the model** via a Power Query M `Table.FromRows` expression and no local-file dependency. Some versions may ask you to enable PBIP preview features or to upgrade the model.
2. Refresh the model (if a dialog prompts), inspect `Readings` in the model pane and confirm dates/PM2.5 types.
3. The *Air quality · Synthetic demo* page contains two KPI cards and a time series. The *Station coverage · Synthetic demo* page contains a station comparison and source table.
4. If desired, replace the `Readings` Power Query M expression with your approved real-source export, preserve `date`, `station`, `pm25`, `source` types, and update labels to identify verified provider data. Never mislabel a demo as observed.
5. After successful open and refresh, **File → Save as → Power BI Desktop (.pbix)** if you specifically need the binary PBIX format. This environment cannot create or verify the binary without Desktop.

## Verification limitations
- JSON structure checked programmatically, not Power BI Desktop runtime compatibility.
- Synthetic data are not real measured PM2.5 values; no official AQI, heat warnings or clinical guidance.
- On real data, verify licensing, daily aggregation period, timestamp timezone and station coverage.

Sources: [Microsoft PBIP projects](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview), [Microsoft PBIR format](https://learn.microsoft.com/en-us/power-bi/developer/embedded/projects-enhanced-report-format).


## Automated source-integrity check

`python -m scripts.verify_powerbi_project` checks PBIP/PBIR JSON, page ordering, required semantic fields and visual measure references in CI. These checks **cannot test Power BI Desktop rendering, data refresh or PBIX export**. See [release acceptance](../docs/RELEASE_ACCEPTANCE.md).
