# Data dictionary

| Field | Description | Type/unit |
|---|---|---|
| `date` | UTC daily bin label from OpenAQ period start or synthetic day | ISO YYYY-MM-DD |
| `station` | OpenAQ location ID or `DEMO-*` generated point | string |
| `sensor` | OpenAQ sensor ID or synthetic ID | string |
| `pm25` | Daily PM2.5 concentration mean for that location | µg/m³ |
| `parameter` | The recorded pollutant parameter | `pm25` |
| `source` | Real source or explicit synthetic origin | string |
| `units` | Pollutant unit | µg/m³ |
| `temperature_c` | Weather grid-model current air temperature | °C |
| `humidity_pct` | Weather grid-model relative humidity | % |
| `apparent_temperature_c` | Weather grid-model feels-like temperature | °C |
| `kind` | Record type (`synthetic`, `daily_observed_aggregate`, or `forecast`) | categorical |

**Caution:** UTC bins can differ from OpenAQ's local-day aggregation. Treat date labels as provenance markers for the API's daily period; do not imply midnight-to-midnight UTC coverage unless the source confirms it. Attribution and source license metadata should be reviewed before redistribution.
