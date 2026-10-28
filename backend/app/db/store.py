"""Optional auditable local snapshots for data inspection and SQL examples."""
import sqlite3
from pathlib import Path

SCHEMA = """CREATE TABLE IF NOT EXISTS readings (
  city TEXT NOT NULL, day TEXT NOT NULL, station TEXT NOT NULL,
  pm25 REAL NOT NULL CHECK (pm25 >= 0), source TEXT NOT NULL,
  PRIMARY KEY (city, day, station)
);"""


def save_frame(db_path, city, frame):
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as con:
        con.execute(SCHEMA)
        con.executemany("""INSERT INTO readings (city,day,station,pm25,source)
            VALUES (?,?,?,?,?) ON CONFLICT(city,day,station) DO UPDATE SET
            pm25=excluded.pm25,source=excluded.source""",
            ((city, str(row.date), str(row.station), float(row.pm25), str(row.source))
             for row in frame.itertuples(index=False)))


def daily_average(db_path, city):
    with sqlite3.connect(db_path) as con:
        return con.execute("""SELECT day, ROUND(AVG(pm25),2), COUNT(DISTINCT station)
            FROM readings WHERE city = ? GROUP BY day ORDER BY day""", (city,)).fetchall()
