.. tiletanic documentation master file, created by
   sphinx-quickstart on Mon Nov  2 15:35:27 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Tiletanic: Tools for Manipulating Geospatial Tiling Schemes
===========================================================

Tiletanic is a library for making and using geospatial tiling schemes.  It's goal is to provide tooling for dealing with the conversion between a tile specified in  as (row, column, zoom level),  geospatial coordinates, or quadkeys.  It also provides functionaly for taking an input geometry and figuring out what tiles cover it.  

Tiletanic is MIT licensed.

Contributions are more than welcome!  Please check out the `GitHub site`_.

Installation is easy::

    pip install tiletanic

The only dependency is shapely_, and to install that, you'll need GEOS_ installed (usually in your package manager). 

.. toctree::
   :maxdepth: 2
   
   motivation
   user_guide
   tiletanic

.. _`GitHub site`: https://github.com/DigitalGlobe/tiletanic
.. _shapely: https://github.com/Toblerity/Shapely
.. _GEOS: http://geos.osgeo.org/doxygen/
