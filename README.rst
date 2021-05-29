SAVSNet data aggregation package
================================

**Purpose**: This package provides functions to aggregate SAVSNet consult linelisting data
by week and geography.

**Author**: Chris Jewell <c.jewell@lancaster.ac.uk>

**License**: MIT

**Copyright**: Chris Jewell 2021


`savsnet-geoaggregation` provides tools to ingest SAVSNet linelists of consults, and
aggregate them by week and geography.  The aim is to provide total numbers of consults and
numbers of consults with major presenting complains per week per geography for
spatio-temporal analysis.  By default, consults are aggregated to UK Local Authority
District 2020 geographies, provided freely by the `Office for National Statistics Geoportal`_.
The package can be used in two ways, from the command line and programmatically, as described below.

.. _Office for National Statistics Geoportal: https://geoportal.statistics.gov.uk/datasets/bc2820b03de244698c0b0771ae4f345f_0

Installation
============

The recommended way to install ``savsnet-geoaggregation`` is via ``pip``

.. code-block:: bash
		
  pip install git+https://github.com/chrism0dwk/savsnet-geoaggregate.git

For users wishing to fork and develop the package, we use the
`poetry`_ build system.  It is recommended to have this installed
when developing in order to install the correct dependencies into a Python virtual
environment.  Regular users of the package may safely disregard this paragraph!

.. _poetry: https://pypoetry.org

Command line usage
==================

``savsnet-geoaggregation`` provides a command line utility ``savsnet-aggregate``.  This is
used like so

.. code-block:: bash

		$ savsnet-aggregate --mpc gastroenteric,respiratory,pruritis \
		    --output foo.txt linelisting.csv

which will read in ``linelisting.csv``, write to ``foo.csv``, and summarise the gastroenteric,
respiratory, and pruritus major presenting complaints.

Detailed usage can be found by running

.. code-block:: bash
		
		$ savsnet-aggregate -h


Programmatic usage
==================

To use ``savsnet-geoaggregation`` from within a Python script, you will need a `Pandas <https://pandas.pydata.org>` ``DataFrame`` containing linelisting data, indexed by date and with columns ``mpc``, ``longitude`` and ``latitude``.

The package provides UK Local Authority District polygons as a built-in dataset accessible via the
``geographies()`` function.  You can provide your own geographies as a `GeoPandas <https://geopandas.org>`` ``GeoDataFrame`` object, using an identical schema to that returned by ``geographies()``.

A worked example might be:

.. code-block:: python

   import pandas as pd
   from savsnet_geoaggregation import aggregate
   from savsnet_geoaggregation import geographies

   # Load geographies
   geo = geographies()

   # Load linelisting
   linelist = pd.read_csv("/path/to/linelisting.csv")

   # Define major presenting conditions as required
   mpcs = ['gastroenteric', 'respiratory', 'pruritus']

   # Perform the aggregation
   df = aggregate(linelist, geo, mpcs)

