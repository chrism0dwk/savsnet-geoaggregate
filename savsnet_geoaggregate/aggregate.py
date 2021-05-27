"""Aggregates SAVSNet linelisting data by week and
geography"""

from typing import List
import pkg_resources

import pandas as pd
import geopandas as gp

from savsnet_geoaggregate import config

CSV_COLS = ["consult_date", "mpc", "owner_latitude", "owner_longitude"]


def _load_mpc_csv(filename: str) -> pd.DataFrame:
    linelisting = (
        pd.read_csv(
            filename,
            parse_dates=[CSV_COLS[0]],
            index_col=[CSV_COLS[0]],
            usecols=CSV_COLS,
        )
        .sort_index()
        .rename(
            columns={
                "owner_latitude": "latitude",
                "owner_longitude": "longitude",
            }
        )
    )
    linelisting.index.name = "date"
    return linelisting


def aggregate(
    linelist: pd.DataFrame, geographies: gp.GeoDataFrame, mpc_list: List[str]
) -> pd.DataFrame:
    """Provides counts of values in `mpcs` present in `linelist['mpc']` 
       aggregated by week and geography. 

    :param linelist: a Pandas DataFrame with columns ["date", "mpc", 
                     "longitude", "latitude"] 
    :param geographies: a GeoPandas GeoDataFrame with columns ['label', 'geometry']
    :param mpc: a list of values in `linelist['mpc']` for which aggregation is required.
    :returns: a Pandas DataFrame indexed by location code and week
              with mpc columns and total counts.
    """
    # Merge polygon data into linelisting data
    geo_ll = gp.GeoDataFrame(
        linelist["mpc"].reset_index(),
        geometry=gp.points_from_xy(linelist["longitude"], linelist["latitude"]),
        crs="EPSG:4326",
    )
    geo_ll = gp.sjoin(geo_ll, geographies, how="left", op="within",)

    # Create a list of required aggregations
    def count(m):
        def fn(x):
            return sum(x == m)

        return fn

    aggregations = [("total_count", "size")]
    for m in mpc_list:
        aggregations.append((m, count(m)))

    # Aggregate
    agg = geo_ll.groupby(["label", "date"]).agg({"mpc": aggregations})
    agg.columns = agg.columns.droplevel(level=0)

    return agg
