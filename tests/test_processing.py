import pandas as pd
import pytest
from src.airaware.processing.clean import normalize_openaq_days
from src.airaware.processing.validation import validate_measurements,coverage
from src.airaware.processing.features import daily_city_average,make_features,join_weather
from src.airaware.ingestion.demo import demo_readings
from src.airaware.monitoring.anomalies import anomalies
from src.airaware.models.train import train_and_evaluate
from src.airaware.models.predict import forecast
from backend.app.service import heat_band


def test_normalize_known_schema():
    rows=[{"period":{"datetimeFrom":{"utc":"2026-10-20T00:00:00Z"}},"value":13.4}]
    result=normalize_openaq_days(rows,'42','88')
    assert result[0]['date']=='2026-10-20' and result[0]['pm25']==13.4


def test_normalize_incompatible_units():
    assert normalize_openaq_days([{"value":12}], 'a','b','ppm')==[]


def test_validation_removes_bad_values():
    frame=pd.DataFrame([{'date':'2026-01-01','station':'A','pm25':12},{'date':'2026-01-02','station':'A','pm25':-5},
                        {'date':'bad','station':'A','pm25':7}])
    assert len(validate_measurements(frame))==1


def test_missing_coverage():
    frame=demo_readings('Hyderabad',20)
    valid=validate_measurements(frame)
    info=coverage(valid,20)
    assert 0 < info['coverage_pct'] <= 100


def test_features_have_prior_day_lag():
    df=pd.DataFrame({'date':pd.date_range('2026-01-01',periods=20,freq='D',tz='UTC'),'pm25':range(20)})
    result=make_features(df)
    assert result.iloc[0]['lag1']==6 and result.iloc[0]['lag7']==0


def test_weather_join_preserves_missing():
    pm=pd.DataFrame({'date':['2026-01-01','2026-01-02'],'pm25':[10,20]})
    w=pd.DataFrame({'date':['2026-01-01'],'temperature_c':[30]})
    out=join_weather(pm,w)
    assert len(out)==2 and pd.isna(out.iloc[1].temperature_c)


def test_heat_band():
    assert heat_band(None)=='unavailable'
    assert heat_band(41)=='very high' and heat_band(29)=='elevated'


def test_no_future_values_in_forecast():
    demo=validate_measurements(demo_readings('Hyderabad',30))
    values=forecast(demo,3)
    assert all(row['kind']=='forecast' for row in values)
    assert values[0]['date']>str(demo.date.max().date())


def test_train_evaluation_is_synthetic():
    metrics=train_and_evaluate('Delhi')
    assert metrics['data_mode']=='synthetic_demo' and metrics['test_rows']>0
    assert metrics['baseline']['mae']>=0 and metrics['random_forest']['rmse']>=0


def test_anomalies_empty():
    assert anomalies(pd.DataFrame())==[]
