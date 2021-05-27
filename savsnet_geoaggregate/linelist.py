"""Linelist-related functions"""

import pandas as pd

from savsnet_geoaggregate import config


def load_linelist(linelist):
    df = (
        pd.read_csv(
            linelist,
            parse_dates=[config.LL_COLUMN_DATE],
            index_col=[config.LL_COLUMN_DATE],
            usecols=config.LL_COLUMNS,
        )
        .sort_index()
        .rename(
            columns={
                config.LL_COLUMN_LATITUDE: "latitude",
                config.LL_COLUMN_LONGITUDE: "longitude",
            }
        )
    )
    df.index.name = "date"
    return df
