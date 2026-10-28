from backend.app.db.store import save_frame,daily_average
from src.airaware.ingestion.demo import demo_readings


def test_storage_idempotent(tmp_path):
    path=tmp_path/'db.sqlite'
    frame=demo_readings('Hyderabad',8)
    save_frame(path,'Hyderabad',frame)
    first=daily_average(path,'Hyderabad')
    save_frame(path,'Hyderabad',frame)
    second=daily_average(path,'Hyderabad')
    assert first==second and len(first)==8


def test_sql_parameterization(tmp_path):
    path=tmp_path/'db.sqlite'
    save_frame(path,'Hyderabad',demo_readings('Hyderabad',4))
    assert daily_average(path, "Hyderabad' OR 1=1--")==[]
