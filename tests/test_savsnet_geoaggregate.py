"""Tests"""
import pytest

import pandas as pd
import geopandas as gp

from savsnet_geoaggregate import config

from io import StringIO


@pytest.fixture
def examplecsv(tmpdir_factory):
    """Create an example CSV file"""

    CSVCONTENT = f"""{config.LL_COLUMN_DATE},{config.LL_COLUMN_MPC},{config.LL_COLUMN_LONGITUDE},{config.LL_COLUMN_LATITUDE},{config.LL_COLUMN_SPECIES}
1970-01-01,mastics,-3.806693,53.785583,triceratops
1970-01-02,salanders,-3.806693,53.785583,triceratops
1970-01-03,malanders,-3.806693,53.785583,triceratops
1970-01-04,flopbot,-3.806693,53.785583,triceratops
1970-01-05,flopbot,-3.806693,53.785583,triceratops
1970-01-01,mastics,-3.806693,53.785583,icthyosaur
1970-01-02,salanders,-3.806693,53.785583,icthyosaur
1970-01-03,malanders,-3.806693,53.785583,icthyosaur
1970-01-04,flopbot,-3.806693,53.785583,icthyosaur
1970-01-05,flopbot,-3.806693,53.785583,icthyosaur

"""
    tmpfile = tmpdir_factory.mktemp("data").join("data.csv")
    with open(tmpfile, "w") as f:
        f.write(CSVCONTENT)
    return tmpfile


@pytest.fixture
def example_df():
    """ some test points in the middle of a unit square """
    StringData = StringIO(
        """mpc,longitude,latitude,date,species
mastics, 0.5, 0.5, 1970-01-01,triceratops
salanders, 0.5, 0.5, 1970-01-02,triceratops
malanders, 0.5, 0.5, 1970-01-03,triceratops
flopbot, 0.5, 0.5, 1970-01-04,triceratops
flopbot, 0.5, 0.5, 1970-01-05,triceratops
mastics, 0.5, 0.5, 1970-01-01,icthyosaur
salanders, 0.5, 0.5, 1970-01-02,icthyosaur
malanders, 0.5, 0.5, 1970-01-03,icthyosaur
flopbot, 0.5, 0.5, 1970-01-04,icthyosaur
flopbot, 0.5, 0.5, 1970-01-05,icthyosaur
"""
    )
    return read_date_index(StringData)


def read_date_index(d):
    df = pd.read_csv(
        d,
        sep=",",
        skipinitialspace=True,
        parse_dates=["date"],
        index_col=["date"],
    )
    return df


@pytest.fixture
def example_geodf():
    """ a unit square as a geodata frame """
    geography = ["POLYGON ((0 0, 1 0, 1 1, 0 1, 0 0))"]
    geoseries = gp.GeoSeries.from_wkt(geography, name="geometry")
    geodf = gp.GeoDataFrame(
        {"location": ["UnitSquare"]}, geometry=geoseries, crs="EPSG:4326"
    )
    return geodf


@pytest.fixture
def example_geodefs():
    """ two squares """
    geography = [
        "POLYGON ((0 0, 1 0, 1 1, 0 1, 0 0))",
        "POLYGON ((1 0, 2 0, 2 1, 1 1, 1 0))",
    ]
    geoseries = gp.GeoSeries.from_wkt(geography, name="geometry")
    geodf = gp.GeoDataFrame(
        {"location": ["UnitSquare", "SecondSquare"]},
        geometry=geoseries,
        crs="EPSG:4326",
    )
    return geodf


@pytest.fixture
def example_aggregate():
    midx = pd.MultiIndex.from_arrays(
        [
            ["UnitSquare"] * 2,
            ["icthyosaur", "triceratops"],
            [pd.to_datetime("1970-01-01")] * 2,
        ],
        names=["location", "species", "date"],
    )
    total_count = [5, 5]
    mastics = [1, 1]
    flopbot = [2, 2]
    df = pd.DataFrame(
        {"total_count": total_count, "mastics": mastics, "flopbot": flopbot,},
        index=midx,
    )
    print(df)
    return df


def test_load_linelist(examplecsv):
    """Test loading of mpc CSV"""

    from savsnet_geoaggregate.linelist import load_linelist

    test_content = load_linelist(examplecsv)

    assert test_content.shape[0] == 10
    assert set(test_content.columns) == set(
        ("mpc", "longitude", "latitude", "species")
    )
    assert test_content.index.name == "date"


def test_geographies():
    from savsnet_geoaggregate import geographies

    geographies()


def test_aggregate(example_df, example_geodf, example_aggregate):
    from savsnet_geoaggregate import aggregate

    df = aggregate(example_df, example_geodf, mpc_list=["mastics", "flopbot"])
    print(df)
    assert df.equals(example_aggregate)
