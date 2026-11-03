from tools.analytics import (
                            most_common_codes_API,
                            routings
                            )
from tools.retrieve_tools import retrieve_common 
import requests
from api.config import settings
from typing import Literal, Any
import pandas as pd

"""
TOOLS core for agentic tools.
Used by mes_agent
"""

def get_date():
    """Return the current date in YYYY-MM-DD format.
    Usage: Added to system promopt
    """
    #NOTE : For testing purposes set to a fixed date
    return '2025-10-06' #dt.datetime.now().strftime("%Y-%m-%d") #to get current date





class MESDataError(Exception):
    pass 

def _fetch_mes_data(data: Literal["faults", "operations"], **filters) -> pd.DataFrame:
    """Fetch MES data from the external API helper.
    """
    params = {k: v for k, v in filters.items() if v is not None}
    try:
        resp = requests.get(f"{settings.DATA_ENDPOINT}/mes/{data}", params=params, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        raise MESDataError(f"MES API request failed: {e}") from e
    return pd.DataFrame(resp.json()["data"])

GroupField = Literal["fault_code", "fault_category", "work_center_key", "work_center_type", "shift", "part_key"]


def get_most_common_codes(
        data: Literal["faults", "operations"], 
        group_by: list[GroupField],
        start_date: str, 
        end_date: str, 
        metric: Literal["count", "duration"]="count", 
        n: int = 10) -> dict:
    """Rank the most common values of one or more MES fields, e.g. most frequent fault codes 
    or work centers with the most downtime.
    
    Args:
        data: Which MES dataset to use.
        group_by: Column(s) to group by, e.g. ["fault_code"] or ["work_center_key", "part_key"]
        start_date: First day included, YYYY-MM-DD
        end_date: Last day included, YYYY-MM-DD
        metric: "count" for how often something happened, "duration" for time lost.
        n: Number of top rows to return
    """
    try:
        df = _fetch_mes_data(data=data, start_date=start_date, end_date=end_date)
    except MESDataError as e:
        return {"error": str(e)}
    if df.empty:
        return {"n_records": 0, "period": [start_date, end_date], "results": []}
    return most_common_codes_API(df, group_by=group_by, metric=metric, n=n)


def get_routings(part_family: str, n: int = 3) -> dict[str, Any]:
    """How parts of a family have been routed in historical MES data, most common routes first. 
    
    Args:
        part_family (str): Part family, e.g. "Turned", "Weldment", "SheetMetal".
        n (int): Number of routes to return
    """
    try:
        df = _fetch_mes_data(data="operations", part_family=part_family)
    except MESDataError as e:
        return {"error": str(e)}
    if df.empty:
        return{"part_family": part_family, "n_jobs": 0, "routes": []}
    return routings(df, part_family, n)

def search_documents(query:str, k:int=5):
    """Search fault logs and reference documents for text related to the query

    Args:
        query: What to search for.
        k: Number of results to return
    
    """
    return retrieve_common(query, k=k)

ANALYTICS = [get_most_common_codes, get_routings]
RETRIEVAL = [search_documents]
