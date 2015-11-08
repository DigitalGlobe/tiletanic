User Guide
==========

Building Blocks
---------------

Tiletanic has extremely simple structures (named tuples) for representing the building blocks that compose tiles.  You don't have to use these, they just make your life a little easier.  Some of the prebaked tiling schemes return these named tuples, but they can be treated as tuples just the same if that's the way you prefer to role.

:class:`Tile <tiletanic.base.Tile>`: Just a named tuple for storing (x, y, z) tile coordinates, which is of course the column, row, and zoom level of the tile.  Note that the origin of the row and column coordinates is sometimes defined in the bottom left or top left of the grid.

.. code-block:: pycon

   >>> from tiletanic import base
   >>> tile = base.Tile(1, 2, 3)
   >>> tile
   Tile(x=1, y=2, z=3)
   >>> tile.x
   1
   >>> tile.y
   2
   >>> tile.z
   3
   >>> tile[0]
   1
   >>> tile[1]
   2
   >>> tile[2]
   3

:class:`Coords <tiletanic.base.Coords>`: Geospatial coordinate pairs (x, y).

.. code-block:: pycon

   >>> base.Coords(0., 1.)
   Coords(x=0.0, y=1.0)

:class:`CoordsBbox <tiletanic.base.CoordsBbox>`: Bounding box coordiantes (xmin, ymin, xmax, ymax) 

.. code-block:: pycon

   >>> base.CoordsBbox(0., 0., 1., 1.)
   CoordsBbox(xmin=0.0, ymin=0.0, xmax=1.0, ymax=1.0)


Tiling Schemes
--------------

Tile schemes are how you convert back and forth from tile coordinates to geospatial coordinates or quadkeys and the like.  They also let you easily traverse the tile structure.  You can use one of the schemes that comes with Tiletanic (see :py:class:`here <tiletanic.tileschemes>`) or build your own.  

If you build your own, you'll want to implement the public API of a tilescheme (see :py:mod:`here <tiletanic.tileschemes.BasicTilingBottomLeft>`) so that you can use the tile algorithms defined around this API.

Here's a Web Mercator tile scheme:

.. code-block:: pycon

   >>> from tiletanic import tileschemes
   >>> tiler = tileschemes.WebMercator()

You can check the bounds for which it is defined:

.. code-block:: pycon

   >>> tiler.bounds
   CoordsBbox(xmin=-20037508.342789244, ymin=-20037508.342789244, xmax=20037508.342789244, ymax=20037508.342789244)

Get the XYZ tile coordinates of a geospatial coordinate at a given zoom level:

.. code-block:: pycon

   >>> t = tiler.tile(14765187.879790928, -3029352.3049981054, 14)
   >>> t
   Tile(x=14228, y=9430, z=14)


How about that tile's parent and children:

.. code-block:: pycon

   >>> tiler.parent(t)
   Tile(x=7114, y=4715, z=13)
   >>> tiler.children(t)
   [Tile(x=28456, y=18860, z=15), Tile(x=28457, y=18860, z=15), Tile(x=28456, y=18861, z=15), Tile(x=28457, y=18861, z=15)]

What are the upper left, bottom right, and bounding box geospatial coordinates of that tile?

.. code-block:: pycon

   >>> tiler.ul(t)
   Coords(x=14763964.887338366, y=-3028129.3125455417)
   >>> tiler.br(t)
   Coords(x=14766410.87224349, y=-3030575.297450669)
   >>> tiler.bbox(t)
   CoordsBbox(xmin=14763964.887338366, ymin=-3030575.297450669, xmax=14766410.87224349, ymax=-3028129.3125455417)

Conversion to and from quadkeys is also supported:

.. code-block:: pycon

   >>> qk = tiler.quadkey(t)
   >>> qk
   '31031132030320'
   >>> tiler.quadkey_to_tile(qk)
   Tile(x=14228, y=9430, z=14)

Tile Covering
-------------

Often times, one is given a geometry and would like to know what tiles at a given zoom level cover it.  Luckily for you, Tiletanic provides just such functionality!  Just define your tile scheme, get a `shapely`_ geometry representing the geometry you'd like covered, and call :py:func:`cover_geometry() <tiletanic.tilecover.cover_geometry>`.  

Here's an example using the previous output tile Tile(x=14228, y=9430, z=14):

.. code-block:: pycon

   >>> from tiletanic import tilecover
   >>> from shapely import geometry
   >>> [t for t in tilecover.cover_geometry(tiler, geometry.box(*tiler.bbox(t)), 14)]
   [Tile(x=14228, y=9430, z=14), Tile(x=14229, y=9430, z=14), Tile(x=14228, y=9431, z=14), Tile(x=14229, y=9431, z=14), Tile(x=14230, y=9430, z=14), Tile(x=14230, y=9431, z=14), Tile(x=14228, y=9432, z=14), Tile(x=14229, y=9432, z=14), Tile(x=14230, y=9432, z=14)]
  
Note that 9 tiles are returned; this is expected as a tile has 8 neighbor tiles that touch it at a given level.  If we try a corner tile at that same level, we get back four tiles as expected:

.. code-block:: pycon

   >>> [t for t in tilecover.cover_geometry(tiler, geometry.box(*tiler.bbox(0,0,14)), 14)]
   [Tile(x=0, y=0, z=14), Tile(x=1, y=0, z=14), Tile(x=0, y=1, z=14), Tile(x=1, y=1, z=14)]

:py:func:`cover_geometry() <tiletanic.tilecover.cover_geometry>` works with all the shapely geometry types (Points, Polygons, and LineStrings as well as their Multi versions).

.. _shapely: https://github.com/Toblerity/Shapely


