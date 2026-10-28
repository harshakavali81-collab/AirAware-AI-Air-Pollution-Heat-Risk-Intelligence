# Model card — exploratory PM2.5 daily forecasting

**Problem:** predict next-day citywide mean PM2.5 in µg/m³ from lagged historical daily aggregates.

**Models:** previous-day persistence vs RandomForestRegressor (120 trees, depth 7, min leaf 3).

**Features:** prior-day value, seven-day lag, trailing seven-day mean shifted by one day, calendar day-of-week. All features reference historical timestamps only.

**Evaluation:** first 80% of valid feature rows for training; last 20% held out by time. MAE and RMSE reported for both models on identical dates. No random train/test shuffling. This is one-day-ahead evaluation with known lag inputs; recursive multi-day performance is NOT validated.

**Dataset:** scripted synthetic values only. Scores measure success on fabricated data and cannot substantiate real-world performance claims. Live-mode training would require independently audited historical data and additional backtests.

**Known limitations:** geographic aggregation can hide local variation; changes to reporting sensors introduce selection bias; missing days are not imputed; weather covariates are not included; non-stationary seasons and wildfire spikes can defeat the model; no uncertainty intervals have been calibrated.

**Safety:** forecasts are separated from observations in the API and UI. No personalized medical or emergency recommendations.
