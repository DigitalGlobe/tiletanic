.. tiletanic documentation master file, created by
   sphinx-quickstart on Mon Nov  2 15:35:27 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Tiletanic: Tools for Manipulating Geospatial Tiling Schemes
===========================================================

Tiletanic is a library for making and using geospatial tiling schemes.  It's goal is to provide tooling for dealing with the conversion between a tile specified in  as (row, column, zoom level),  geospatial coordinates, or quadkeys.  It also provides functionaly for taking an input geometry and figuring out what tiles cover it.  

Motivation
----------

You may be familar with the `Web Mercator`_ (or Spherical Mercator, Google Tiles, etc) tiling scheme, which is the most commonly encountered tiling scheme on the web.  There are good tools out there for dealing specifically with this projection, for instance Mercantile_ fits the bill.  If you're dealing exclusively with this projection, you might get better mileage with them!

One oddity of Web Mercator is that coordinates are usually expressed in geographic (longitude, latitude) coordinates that live on the ellipsoid (WGS84) rather than in units of the Web Mercator projection (meters).  Dealing with this kind of conversion is exactly what Mercantile_ and its like were made to handle.

Tiletanic's use cases are a bit different:

- What do you do if your data is already in some projection?  For instance, you might want to know what tile covers a point specified in the Web Mercator projection without first converting back to WGS84.  Tiletanic can help.
- At DigitalGlobe_, our imagery is often projected into many other projections (UTM, Geographic, etc) and it is often times extremely convienent to organize raster data into a tiled format before proceeding with processing (a single "strip" from one of our satellite collects can easily be 100km long!).  When dealing with different projections, the user typically needs to impose their own tiling scheme.  Tiletanic provides an easy way for you to define you're own scheme and get a lot of tiling functionality right out of the gate.

User Guide
==========

Building Blocks
---------------

Tiletanic has extremely simple structures (named tuples) for representing the building blocks that compose tiles.  You don't have to use these, they just make your life a little easier.  Some of the prebaked tiling schemes return these named tuples, but they can be treated as tuples just the same if that's the way you prefer to role.

:class:`Tile <tiletanic.base.Tile>`: Just a named tuple for storing (x, y, z) tile coordinates, which is of course the column, row, and zoom level of the tile.  Note that the origin of the row and column coordinates is sometimes defined in the bottom left or top left of the grid.

:class:`Coords <tiletanic.base.Coords>`: Geospatial coordinate pairs (x, y).

:class:`CoordsBbox <tiletanic.base.CoordsBbox>`: Bounding box coordiantes (xmin, ymin, xmax, ymax) 

Tiling Schemes
--------------

Tile schemes are how you convert back and forth from tile coordinates to geospatial coordinates or quadkeys and the like.  They also let you easily traverse the tile structure.  You can use one of the schemes that comes with Tiletanic (see :py:class:`here <tiletanic.tileschemes>`) or build your own.  If you build your own, you'll want to implement the public API of a tilescheme (see :py:mod:`here <tiletanic.tileschemes.BasicTilingBottomLeft>`) so that you can use the tile algorithms defined around this API.

Tile Covering
-------------

Often times, one is given a geometry and would like to know what tiles at a given zoom level cover it.  Luckily for you, Tiletanic provides just such functionality!  Just define your tile scheme, get `shapely`_ geometry representing the geometry you'd like covered, and call `:py:function: <tiletanic.tilecover.cover_geometry>`
  
.. _`Web Mercator`: https://en.wikipedia.org/wiki/Web_Mercator
.. _Mercantile: https://github.com/mapbox/mercantile
.. _DigitalGlobe: https://www.digitalglobe.com/
.. _shapely: https://github.com/Toblerity/Shapely

.. toctree::
   :maxdepth: 2



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

