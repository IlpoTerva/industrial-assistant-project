import pandas as pd
import json

"""
MES analytics from MES data
"""

def most_common_codes_API(df: pd.DataFrame, group_by: list[str]|str, metric: str="count", n: int = 10):
    """Return the n most common values for a given field (column) in the MES fault data,
    i.e most common machines that have fault codes, operations that have fault codes, etc.
    Returns a dict of {value: count}, or {"error": ...} if `category` is not a valid field.
    """
    if isinstance(group_by, str):
        group_by = [group_by]

    agg = (df.groupby(group_by, dropna=False).agg(faults=("fault_code", "size"), downtime_min=("duration_minutes", "sum")).reset_index())

    sort_col = "faults" if metric == "count" else "downtime_min"
    agg["downtime_min"] = agg["downtime_min"].round(1)
    agg = agg.sort_values(sort_col, ascending=False).head(n)

    return {
        "metric": metric,
        "group_by": group_by,
        "total_faults": int(len(df)),
        "total_downtime_min": round(float(df["duration_minutes"].sum()), 1),
        "results": json.loads(agg.to_json(orient="records"))
    }


def routings(df: pd.DataFrame, part_family: str, n: int=3) -> dict[list]:
    df.groupby(["job_id", "op_seq"])

    jobs = df.groupby("job_id").agg(
        route=("work_center_key", tuple),
        part_family=("part_family", "first"),
        batch_qty=("batch_qty","first"),
    )

    total = len(jobs)
    routes = []
    for route, g in jobs.groupby("route"):
        routes.append({"route": list(route),
                       "n_jobs": len(g)})
    routes.sort(key=lambda r: r["n_jobs"], reverse=True)

    return {"part_family": part_family, "n_jobs": total,
            "n_distinct_routes": len(routes), "routes": routes[:n]}

