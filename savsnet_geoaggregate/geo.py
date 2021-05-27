"""Package-embedded geographies"""

import pkg_resources
import geopandas as gp


def geographies():
    """Returns a GeoPandas DataFrame with package-embedded default
       geographies.
    :returns: `geopandas.DataFrame`
    """
    geofile = (
        pkg_resources.resource_filename(
            __name__, "/".join(("data", "uk_lad20.gpkg"))
        ),
    )[0]
    gdf = gp.read_file(geofile)
    gdf = gdf[["LAD20CD", "geometry"]]
    gdf = gdf.rename(columns={"LAD20CD": "label"})
    return gdf
