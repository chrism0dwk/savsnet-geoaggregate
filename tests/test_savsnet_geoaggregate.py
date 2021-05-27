"""Tests"""
import pytest

import pandas as pd
import geopandas as gp

from savsnet_geoaggregate import config


@pytest.fixture
def examplecsv(tmpdir_factory):
    """Create an example CSV file"""

    CSVCONTENT = f"""{config.LL_COLUMN_DATE},{config.LL_COLUMN_MPC},{config.LL_COLUMN_LONGITUDE},{config.LL_COLUMN_LATITUDE}
1970-01-01,mastics,-3.806693,53.785583
1970-01-02,salanders,-3.806693,53.785583
1970-01-03,malanders,-3.806693,53.785583
1970-01-04,flopbot,-3.806693,53.785583
1970-01-05,flopbot,-3.806693,53.785583
"""
    tmpfile = tmpdir_factory.mktemp("data").join("data.csv")
    with open(tmpfile, "w") as f:
        f.write(CSVCONTENT)
    return tmpfile


@pytest.fixture
def example_df():
    df = pd.DataFrame(
        {
            "mpc": ["mastics", "salanders", "malanders", "flopbot", "flopbot"],
            "longitude": [-3.806693] * 5,
            "latitude": [53.785583] * 5,
        },
        index=pd.Index(
            pd.to_datetime(
                [
                    "1970-01-01",
                    "1970-01-02",
                    "1970-01-03",
                    "1970-01-04",
                    "1970-01-04",
                ]
            ),
            name="date",
        ),
    )
    return df


@pytest.fixture
def example_geodf():
    geography = [
        "POLYGON ((-3.806 53.785, -3.807 53.785, -3.807 53.786, -3.806 53.786, -3.806 53.785))"
    ]
    geoseries = gp.GeoSeries.from_wkt(geography, name="geometry")
    geodf = gp.GeoDataFrame(
        {"label": ["IrishSea"]}, geometry=geoseries, crs="EPSG:4326"
    )
    return geodf


@pytest.fixture
def example_aggregate():
    midx = pd.MultiIndex.from_product(
        [["IrishSea"], pd.date_range("1970-01-01", "1970-01-04")]
    )
    total_count = [1, 1, 1, 2]
    mastics = [0, 0, 0, 2]
    flopbot = [0, 0, 0, 2]
    return pd.DataFrame(
        {"total_count": total_count, "mastics": mastics, "flopbot": flopbot,},
        index=midx,
    )


def test_load_linelist(examplecsv):
    """Test loading of mpc CSV"""

    from savsnet_geoaggregate.linelist import load_linelist

    test_content = load_linelist(examplecsv)

    assert test_content.shape[0] == 5
    assert set(test_content.columns) == set(("mpc", "longitude", "latitude"))
    assert test_content.index.name == "date"


def test_geographies():
    from savsnet_geoaggregate import geographies

    geographies()


def test_aggregate(example_df, example_geodf, example_aggregate):
    from savsnet_geoaggregate import aggregate

    df = aggregate(example_df, example_geodf, mpc_list=["mastics", "flopbot"])
    assert df.equals(example_aggregate)
