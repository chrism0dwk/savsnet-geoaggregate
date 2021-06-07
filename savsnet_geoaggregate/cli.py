"""Command line utility to run aggregation"""

import argparse
import geopandas as gp

from savsnet_geoaggregate import geographies
from savsnet_geoaggregate import aggregate
from savsnet_geoaggregate import config
from savsnet_geoaggregate.linelist import load_linelist


def _cli_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output", "-o", type=str, help="Output CSV file", required=True
    )
    parser.add_argument(
        "--geo", "-g", type=str, default=None, help="Optional geography file"
    )
    parser.add_argument(
        "--mpc",
        "-m",
        type=str,
        default=None,
        help="Comma-separated list of MPCs to summarise",
    )
    parser.add_argument(
        "Linelist CSV",
        type=str,
        help="SAVSNet linelist CSV with at least columns ['consult_date', 'mpc', 'owner_latitude', 'owner_longitude'",
    )
    return parser.parse_args()


def run():
    """Command line utility to run the aggregation on a CSV
       file.
       
       Example usage:
       ```bash
       $ savsnet_geoaggregate --mpc respiratory pruritus gastroenteric \
            --out sn_aggregated.csv linelist.csv
       ```
    """

    args = _cli_args()

    linelist = load_linelist(getattr(args, "Linelist CSV"))

    if args.geo is None:
        geo = geographies()
    else:
        geo = gp.read_file(args.geo)

    if args.mpc is not None:
        mpc = [s.strip() for s in args.mpc.split(",")]
    else:
        mpc = []

    df = aggregate(linelist, geo, mpc)
    df.to_csv(args.output)


if __name__ == "__main__":
    run()
