"""Aggregates SAVSNet linelisting data by week and
geography"""

from typing import List
import pkg_resources

import pandas as pd
import geopandas as gp

from savsnet_geoaggregate import config

CSV_COLS = [
    "consult_date",
    "mpc",
    "owner_latitude",
    "owner_longitude",
    "species",
]


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


def _spatial_join(points_df, polygon_df, how="inner"):
    """Merge polgon_df into points_df using point in polygon"""
    # TODO: construction of GeoDataFrame is slow -- why?
    geo_ll = gp.GeoDataFrame(
        points_df.reset_index(),
        geometry=gp.points_from_xy(
            points_df["longitude"], points_df["latitude"]
        ),
        crs="EPSG:4326",
    )
    geo_ll = gp.sjoin(geo_ll, polygon_df, how=how, op="within")
    return geo_ll


def _reindex(df, locations, species):
    """df has MultiIndex (date, location, species).  We re-index to ensure
    dates are contiguous, values padded with 0s where dates are missing
    in the original data frame.
    """
    orig_dates = df.index.get_level_values(0)
    date_range = pd.date_range(orig_dates.min(), orig_dates.max())
    index = pd.MultiIndex.from_product((date_range, locations, species))
    index.names = df.index.names
    return df.reindex(index, fill_value=0)


def _count_by_day_loc_species(geo_df, mpc_list):
    """Counts number of linelist records by day/location/species
    according to requested mpcs
    
    :param geo_df: a GeoDataFrame with columns ["date", "location", "mpc", "species"]
    :param mpc_list: a list of mpc strings to match
    :returns: a DataFrame indexed by (`date`, `location`, `species`) containing total record 
    count and counts matching strings in `mpc_list`.
    """

    def count(m):
        def fn(x):
            return sum(x == m)

        return fn

    aggregations = [("total_count", "size")]
    for m in mpc_list:
        aggregations.append((m, count(m)))

    # Aggregate to location/day by species
    agg = geo_df.groupby(["date", "location", "species"]).agg(
        {"mpc": aggregations}
    )
    agg.columns = agg.columns.droplevel(level=0)

    return agg


def aggregate(
    linelist: pd.DataFrame,
    geographies: gp.GeoDataFrame,
    mpc_list: List[str],
    begin_on_sunday=False,
) -> pd.DataFrame:
    """Provides counts of values in `mpcs` present in `linelist['mpc']` 
       aggregated by week and geography. 

    :param linelist: a Pandas DataFrame with columns ["mpc", 
                     "longitude", "latitude", "species"] indexed by "date".
    :param geographies: a GeoPandas GeoDataFrame with columns ['location', 'geometry']
    :param mpc: a list of values in `linelist['mpc']` for which aggregation is required.
    :param begin_on_sunday: if `True`, the week begins on the earliest Sunday
                            represented in the DataFrame.  Otherwise, week begins
                            on the earliest date.
    :returns: a Pandas DataFrame indexed by location code and week
              with mpc columns and total counts.
    """
    geo_ll = _spatial_join(linelist, geographies)
    agg = _count_by_day_loc_species(geo_ll, mpc_list)
    agg = _reindex(
        agg, geographies["location"].unique(), linelist["species"].unique()
    )

    # Aggregate by 7 days
    period = "W" if begin_on_sunday is True else "7D"
    agg = (
        agg.reset_index(level=(1, 2))
        .groupby(["location", "species"])
        .resample(period)
        .sum()
    )

    return agg
