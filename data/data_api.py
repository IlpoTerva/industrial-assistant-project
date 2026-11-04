
from fastapi import FastAPI, HTTPException, Query
import pandas as pd
import json
from enum import Enum

"""
Simple API to fetch MES data from external resource
"""

class Datatype(str, Enum):
    faults= "faults"
    operations = "operations"

def load_data(data: Datatype) -> pd.DataFrame:
    df = pd.read_csv(f"mes/mes_{data.value}.csv", parse_dates=["date"])
    return df

def filter_by_date(df, mask, start, end) -> pd.DataFrame:
    """Filter a DataFrame by start and end dates."""
    if start:
        mask &= df["date"] >= pd.Timestamp(start)
    if end:
        mask &= df["date"] <= pd.Timestamp(end) + pd.Timedelta(days=1)
    return mask, df


app = FastAPI(title="MES data resource")

@app.get("/mes/{data}")
def get_mes_data(data: Datatype, 
                   start_date: str | None = None, 
                   end_date: str | None = None,
                   job_id: str | None = None,
                   part_family: str | None = None,
                   work_center_key: str | None = None,):

    df = load_data(data)
    mask = pd.Series(True, index=df.index)
    if start_date and end_date:
        mask, df = filter_by_date(df, mask, start_date, end_date)
    
    filters = {"job_id": job_id, "part_family": part_family, "work_center_key": work_center_key}
    for name, value in filters.items():
        if value is None:
            continue
        if name not in df.columns:
            return HTTPException(status_code=400, detail=f"Invalid filter: {name}")
        mask &= df[name] == value
    out = df[mask]

    return {"dataset": data.value,
            "count": len(out),
            "data": json.loads(out.to_json(orient="records", date_format="iso"))} 


