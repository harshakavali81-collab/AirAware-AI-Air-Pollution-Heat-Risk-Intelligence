"""The fixture is synthetic only for unit tests; never a performance claim."""
from __future__ import annotations
import numpy as np
import pandas as pd
import pytest
from scripts.india_spatial_temporal_backtest import spatial_temporal_evaluation


def fixture(stations=10, days=365):
    dates = pd.date_range('2024-01-01', periods=days, tz='UTC')
    rows = []
    for station in range(stations):
        for i, date in enumerate(dates):
            if i % 47 == 0:
                continue
            rows.append({'date': date, 'station': f'location-{station:02d}',
                         'pm25': 15.0 + station + 2 * np.sin(i * .1),
                         'source': 'unit-test clean recorded source fixture'})
    return pd.DataFrame(rows)


def test_disjoint_station_and_time_windows():
    r = spatial_temporal_evaluation(fixture())
    assert r['train_station_count'] == 8
    assert len(r['heldout_stations']) == 2
    assert r['training_rows'] > 200
    assert r['test_rows'] > 50
    assert r['train_date_end'] < r['test_date_start']
    assert r['results']['network_previous_day']['n'] == r['test_rows']
    assert isinstance(r['candidate_beats_baseline'], bool)


def test_selection_is_deterministic_independent_of_input_row_order():
    x=fixture()
    a=spatial_temporal_evaluation(x)
    b=spatial_temporal_evaluation(x.sample(frac=1,random_state=36))
    assert a['heldout_stations'] == b['heldout_stations']
    assert a['results'] == b['results']


def test_synthetic_marked_source_is_rejected():
    x=fixture();x['source']='synthetic fixture'
    with pytest.raises(ValueError,match='Synthetic'):
        spatial_temporal_evaluation(x)


def test_fewer_than_five_stations_rejected():
    with pytest.raises(ValueError, match='five'):
        spatial_temporal_evaluation(fixture(stations=3))


def test_duplicate_station_dates_rejected():
    x=fixture();x=pd.concat([x,x.iloc[[5]]],ignore_index=True)
    with pytest.raises(ValueError,match='Duplicate'):
        spatial_temporal_evaluation(x)


def test_calendar_cutoff_is_checked():
    with pytest.raises(ValueError,match='separate'):
        spatial_temporal_evaluation(fixture(),cutoff=pd.Timestamp('2025-01-01',tz='UTC'))


def test_truncated_sample_rejected_for_low_future_coverage():
    with pytest.raises(ValueError,match='future-covered'):
        spatial_temporal_evaluation(fixture(days=305))


def test_invalid_concentrations_fail_closed():
    x=fixture();x.loc[x.index[0],'pm25']=2500
    with pytest.raises(ValueError,match='Invalid'):
        spatial_temporal_evaluation(x)
