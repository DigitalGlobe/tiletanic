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

Often times, one is given a geometry and would like to know what tiles at a given zoom level cover it.  Luckily for you, Tiletanic provides just such functionality!  Just define your tile scheme, get a `shapely`_ geometry representing the geometry you'd like covered, and call :py:func:`cover_geometry() <tiletanic.tilecover.cover_geometry>`.  
  
.. _shapely: https://github.com/Toblerity/Shapely


