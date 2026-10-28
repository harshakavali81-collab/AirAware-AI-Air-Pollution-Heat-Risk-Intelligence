"""Historical-only Hyderabad PM2.5 generalization check with unseen stations.

Strictly time- and station-disjoint train/test: training stations before cutoff,
held-out monitoring stations on or after cutoff, lagged network aggregates built
*only* from training stations. This is NOT a real-time Indian forecast.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

from scripts.india_cpcb_historical_benchmark import download_hyderabad_2024, import_station_days, SOURCE

SOURCE_KIND = 'xkdr_historical_cpcb_observations'  # only when actually downloaded
CUTOFF = pd.Timestamp('2024-10-01', tz='UTC')
FEATURES = ['network_previous_day', 'year_sin', 'year_cos']


def _errors(actual: np.ndarray, prediction: np.ndarray) -> dict:
    e = np.asarray(actual, dtype=float) - np.asarray(prediction, dtype=float)
    return {'mae': round(float(np.mean(np.abs(e))), 4),
            'rmse': round(float(np.sqrt(np.mean(e * e))), 4),
            'n': int(len(e))}


def spatial_temporal_evaluation(frame: pd.DataFrame, *, cutoff: pd.Timestamp = CUTOFF,
                                min_rows_per_test_station: int = 35) -> dict:
    """Evaluate held-out stations in a later calendar period, never mixing targets.

    The holdout is predeclared by a deterministic hash of station IDs, *not*
    selected for performance. The previous-day network mean uses only training
    stations; no same-day target, test-station history, or future data leaks in.
    """
    if not {'date', 'station', 'pm25'}.issubset(frame):
        raise ValueError('Missing date/station/pm25 columns')
    if frame.empty:
        raise ValueError('No station observations')
    if 'source' in frame and frame.source.astype(str).str.contains('synthetic|demo|fake|fabricat', case=False).any():
        raise ValueError('Synthetic data are not permitted in the observed-data evaluator')

    x = frame[['date', 'station', 'pm25']].copy()
    x['date'] = pd.to_datetime(x.date, utc=True, errors='coerce')
    x['station'] = x.station.astype(str).str.strip()
    x['pm25'] = pd.to_numeric(x.pm25, errors='coerce')
    if x.isna().any().any() or (x.station == '').any() or not x.pm25.between(0, 2000).all():
        raise ValueError('Invalid station, datetime or PM2.5 concentration')
    if x.duplicated(['date', 'station']).any():
        raise ValueError('Duplicate station-day; run import_station_days first')
    if not (x.date.dt.hour == 0).all() or not (x.date.dt.minute == 0).all():
        raise ValueError('Only daily calendar dates allowed')
    if cutoff.tzinfo is None:
        raise ValueError('Cutoff must be timezone aware')
    cutoff = cutoff.tz_convert('UTC')
    if x.date.min() >= cutoff or x.date.max() < cutoff:
        raise ValueError('Cutoff must separate past training and future test dates')

    # Each prospective test station must be represented for >=35 actual future
    # days; selecting on coverage is disclosed, then hash decides holdout.
    future_counts = x.loc[x.date >= cutoff].groupby('station').size()
    eligible = sorted(future_counts[future_counts >= min_rows_per_test_station].index)
    if len(eligible) < 5:
        raise ValueError('At least five future-covered stations needed for unseen-station holdout')
    ranked = sorted(eligible, key=lambda s: hashlib.sha256(s.encode('utf-8')).hexdigest())
    n_holdout = max(1, len(eligible) // 5)
    heldout = ranked[:n_holdout]
    known = sorted(set(x.station) - set(heldout))
    if set(heldout).intersection(known):
        raise AssertionError('Training and held-out stations overlap')
    network = x[x.station.isin(known)].groupby('date').pm25.mean().sort_index()
    calendar = pd.date_range(x.date.min(), x.date.max(), freq='D', tz='UTC')
    # Calendar-aware shift: a gap remains NA instead of accidentally using a
    # value from several days ago.
    prior_network = network.reindex(calendar).shift(1)
    daily = pd.DataFrame({'date': calendar, 'network_previous_day': prior_network.to_numpy()})
    daily['year_sin'] = np.sin(2 * np.pi * daily.date.dt.dayofyear / 365.25)
    daily['year_cos'] = np.cos(2 * np.pi * daily.date.dt.dayofyear / 365.25)
    samples = x.merge(daily, on='date', how='left').dropna(subset=FEATURES)
    train = samples[(samples.station.isin(known)) & (samples.date < cutoff)].sort_values(['date', 'station']).copy()
    test = samples[(samples.station.isin(heldout)) & (samples.date >= cutoff)].sort_values(['date', 'station']).copy()
    if len(train) < 240 or len(test) < n_holdout * min_rows_per_test_station:
        raise ValueError('Insufficient train/test rows after lagging')
    if train.date.max() >= test.date.min() or set(train.station) & set(test.station):
        raise AssertionError('Chronological or station isolation failed')
    model = RandomForestRegressor(n_estimators=80, max_depth=7,
                                  min_samples_leaf=4, random_state=42, n_jobs=1)
    model.fit(train[FEATURES], train.pm25)
    y = test.pm25.to_numpy(dtype=float)
    baseline = test.network_previous_day.to_numpy(dtype=float)
    rf = np.maximum(0, model.predict(test[FEATURES]))
    comparison = {'network_previous_day': _errors(y, baseline),
                  'random_forest_unseen_station': _errors(y, rf)}
    per_station = {}
    for station in heldout:
        mask = (test.station == station).to_numpy()
        per_station[station] = {'network_previous_day': _errors(y[mask], baseline[mask]),
                                'random_forest_unseen_station': _errors(y[mask], rf[mask])}
    return {
        'evaluation_kind': 'historical_2024_unseen_station_future_window_exploratory',
        'data_scope': 'Hyderabad, India, 2024 daily observed PM2.5 from XKDR/CPCB',
        'units': 'µg/m³',
        'training_cutoff_exclusive': cutoff.date().isoformat(),
        'train_station_count': len(set(train.station)), 'heldout_stations': heldout,
        'holdout_rule': 'SHA256-rank station IDs with >=35 future-day readings; first floor(n/5), minimum one',
        'training_rows': len(train), 'test_rows': len(test),
        'train_date_end': train.date.max().date().isoformat(),
        'test_date_start': test.date.min().date().isoformat(),
        'test_date_end': test.date.max().date().isoformat(),
        'predictor_description': 'previous calendar day mean of training stations only, plus known day-of-year phase',
        'reference_baseline': 'previous calendar day mean of training stations only',
        'results': comparison, 'per_station': per_station,
        'candidate_beats_baseline': comparison['random_forest_unseen_station']['mae'] < comparison['network_previous_day']['mae'],
        'verification': 'observed_historical_backtest_not_external_operational_validation',
        'limitations': [
            'No future 2026 measurements; not OpenAQ; cannot certify a live India forecasting service.',
            'Spatial holdout is deterministic but station coverage eligibility uses availability of test period only.',
            'Lagged network mean includes training-station measurements from test dates (available at prediction date -1); no test-station values.',
            'This is a station-level prediction task, not the city-average task used in the original rolling-origin benchmark.',
            'One season and one metro cannot prove safe operational forecasts, future transfer or calibration.',
            'Station calibration, source licensing and independent epidemiological validity have not been independently audited.',
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument('--download-xkdr-2024', action='store_true')
    src.add_argument('--csv', type=Path, help='Local fixture, not source-verified')
    parser.add_argument('--output', type=Path, default=Path('reports/hyderabad_cpcb_spatial_temporal_2024.json'))
    args = parser.parse_args()
    if args.download_xkdr_2024:
        blob, headers = download_hyderabad_2024()
        origin = SOURCE_KIND
    else:
        blob, headers = args.csv.read_bytes(), {}
        origin = 'unverified_local_fixture'
    frame, metadata = import_station_days(blob)
    report = spatial_temporal_evaluation(frame)
    report['data_provenance'] = {'kind': origin, 'source': SOURCE,
                                 'sha256_download': hashlib.sha256(blob).hexdigest(),
                                 'provider_headers': headers, 'input_metadata': metadata}
    report['evaluated_at_utc'] = datetime.now(timezone.utc).isoformat()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    print(json.dumps({'output': str(args.output), 'source': origin,
                      'test_rows': report['test_rows'], 'results': report['results']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
