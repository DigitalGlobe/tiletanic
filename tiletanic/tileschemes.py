"""Tiling schemes precanned for Tiletanic.

The public APIs of these classes are all that another class would need
to implement in order to use any of the algorithms defined in the
Tiletanic package.
"""
from math import floor, ceil, log2
import re

from . import Tile, Coords, CoordsBbox

qk_regex = re.compile(r'[0-3]+$')

class BasicTilingBottomLeft(object):
    """BasicTilingBottomLeft is a class for representing a tiling
    scheme defined by some bounding box.  The x direction considered
    "left" to "right" and the y direction is considered "bottom" to
    "top" when we thing of both geospatial and tile-centric
    coordinates.

    Note that quadkey indices are defined like this for each
    tile's children::

        ---------
        | 2 | 3 |
        --------
        | 0 | 1 |
        ---------

    The origin of a tile (row, column) is the bottom left of the
    bounds, as opposed to some of the web mercator schemes!

    Attributes:
        bounds: The bounding box for the projection that the tiling
                scheme is defined for.
    """
    def __init__(self, xmin, ymin, xmax, ymax):
        """Constructs an object that generates tile bounds for you.

        BasicTilingBottomLeft(-180, -90, 180, 270) would give you a
        square tiling scheme defined over those bounds.  Note that if
        we think of long/lat, we are covering the earth twice with
        such a scheme!

        Args:
            xmin: Minimum geospatial extent in the x direction of
                  tiling scheme.
            ymin: Minimum geospatial extent in the y direction of
                  tiling scheme.
            xmax: Maximum geospatial extent in the x direction of
                  tiling scheme.
            ymax: Maximum geospatial extent in the y direction of
                  tiling scheme.
        """
        if xmax <= xmin:
            raise ValueError("xmax must be greater than xmin")
        if ymax <= ymin:
            raise ValueError("ymax must be greater than ymin")

        # Sometimes, the public bounds aren't the same as the
        # functional ones, as in the case of the dg tiling scheme.
        self._bounds = CoordsBbox(float(xmin), float(ymin),
                                  float(xmax), float(ymax))
        self.bounds = CoordsBbox(float(xmin), float(ymin),
                                 float(xmax), float(ymax))

    def tile(self, xcoord, ycoord, zoom):
        """Returns the (x, y, z) tile at the given zoom level that
        contains the input coordinates.

        Args:
            xcoord: x direction geospatial coordinate within the tile
                    we want.
            ycoord: y direction geospatial coordinate within the tile
                    we want.
            zoom: zoom level of the tile we want.

        Returns:
            A Tile object that covers the given coordinates at the
            provided zoom level.
        """
        return Tile(x=self._x(xcoord, zoom),
                    y=self._y(ycoord, zoom),
                    z=zoom)


    def parent(self, *tile):
        """Returns the parent of the (x, y, z) tile.

        Args:
            *tile: (x, y, z) tile coordinates or a Tile object we want
                   the parent of.

        Returns:
            A Tile object representing the parent of the input.
        """
        if len(tile) == 1: # Handle if a Tile object was inputted.
            tile = tile[0]
        x, y, z = tile

        if x % 2 == 0 and y % 2 == 0: # x and y even
            return Tile(x//2, y//2, z - 1)
        elif x % 2 == 0: # x even, y odd
            return Tile(x//2, (y - 1)//2, z - 1)
        elif y % 2 == 0: # x odd, y even
            return Tile((x - 1)//2, y//2, z - 1)
        else: # x odd, y odd
            return Tile((x - 1)//2, (y - 1)//2, z - 1)


    def children(self, *tile):
        """Returns the children of the (x, y, z) tile.

        Args:
            *tile: (x, y, z) tile coordinates or a Tile object we want
                   the children of.

        Yields:
            An iterable of Tile objects representing the children of
            this tile.
        """
        if len(tile) == 1: # Handle if a Tile object was inputted.
            tile = tile[0]
        x, y, z  = tile

        return [Tile(2*x, 2*y, z + 1),
                Tile(2*x + 1, 2*y, z + 1),
                Tile(2*x, 2*y + 1, z + 1),
                Tile(2*x + 1, 2*y + 1, z + 1)]


    def ul(self, *tile):
        """Returns the upper left coordinate of the (x, y, z) tile.

        Args:
            *tile: (x, y, z) tile coordinates or a Tile object we want
                   the upper left geospatial coordinates of.

        Returns:
            The upper left geospatial coordiantes of the input tile.
        """
        if len(tile) == 1: # Handle if a Tile object was inputted.
            tile = tile[0]
        x, y, z  = tile

        return Coords(self._xcoord(x, z), self._ycoord(y + 1, z))


    def br(self, *tile):
        """Returns the bottom right coordinate of the (x, y, z) tile.

        Args:
            *tile: (x, y, z) tile coordinates or a Tile object we want
                   the bottom right geospatial coordinates of.

        Returns:
            The bottom right geospatial coordiantes of the input tile.
        """
        if len(tile) == 1: # Handle if a Tile object was inputted.
            tile = tile[0]
        x, y, z  = tile

        return Coords(self._xcoord(x + 1, z),
                      self._ycoord(y, z))


    def bbox(self, *tile):
        """Returns the bounding box of the (x, y, z) tile.

        Args:
            *tile: A tuple of (x, y, z) tile coordinates or a Tile
                   object we want the bounding box of.

        Returns:
            The bounding box of the input tile.
        """
        if len(tile) == 1: # Handle if a Tile object was inputted.
            tile = tile[0]
        x, y, z  = tile

        west, north = self.ul(tile)
        east, south = self.br(tile)
        return CoordsBbox(west, south, east, north)


    def quadkey(self, *tile):
        """Returns the quadkey of the (x, y, z) tile.

        Args:
            *tile: A tuple of (x, y, z) tile coordinates or a Tile
                   object we want the quadkey of.

        Returns:
            The quadkey of the input tile.
        """
        if len(tile) == 1: # Handle if a Tile object was inputted.
            tile = tile[0]
        x, y, z  = [int(i) for i in tile]

        quadkey = []
        for zoom in range(z, 0, -1):
            digit = 0
            mask = 1 << (zoom - 1)
            if int(x) & mask:
                digit += 1
            if int(y) & mask:
                digit += 2
            quadkey.append(digit)
        return ''.join(str(d) for d in quadkey)


    def quadkey_to_tile(self, qk):
        """Returns the Tile object represented by the input quadkey.

        Args:
            qk: A string representing the quadkey.

        Returns:
            The Tile object represented by the input quadkey.
        """
        if not qk_regex.match(qk):
            raise ValueError("Input quadkey is invalid.")

        x = 0
        y = 0
        for i, digit in enumerate(reversed(qk)):
            mask = 1 << i
            if digit == '1':
                x = x | mask
            elif digit == '2':
                y = y | mask
            elif digit == '3':
                x = x | mask
                y = y | mask
        return Tile(x, y, len(qk))

    def _xcoord(self, x, z):
        """Left geospatial coordinate of tile at given column and zoom.

        Args:
            x: The tile's column coordinate.
            z: The zoom level.

        Returns:
            The left geospatial coordinate of this tile.
        """
        return ((x/(2.**z)*(self._bounds.xmax - self._bounds.xmin)) + self._bounds.xmin)


    def _ycoord(self, y, z):
        """Bottom geospatial coordinate of tile at given row and zoom.

        Args:
            y: The tile's row coordinate.
            z: The zoom level.

        Returns:
            The bottom geospatial coordinate of this tile.
        """

        return ((y/(2.**z)*(self._bounds.ymax - self._bounds.ymin)) + self._bounds.ymin)


    def _x(self, xcoord, zoom):
        """Get the x coordinate (column) of this tile at this zoom level.

        Args:
            xcoord: x coordinate to covert to tile index.
            zoom: zoom level of th tile we want.

        Returns:
            The x coordinate (column) of the tile.
        """
        return int(floor((2.**zoom)*(xcoord - self._bounds.xmin)/(self._bounds.xmax - self._bounds.xmin)))


    def _y(self, ycoord, zoom):
        """Get the y coordinate (row) of this tile at this zoom level.

        Note that this function assumes that the origin is on the
        bottom, not the top!

        Args:
            ycoord: y coordinate to covert to tile index.
            zoom: zoom level of th tile we want.

        Returns:
            The y coordinate (row) of the tile.
        """
        return int(floor((2.**zoom)*(ycoord - self._bounds.ymin)/(self._bounds.ymax - self._bounds.ymin)))


class BasicTilingTopLeft(object):
    """BasicTilingTopLeft is a class for representing a tiling
    scheme defined by some bounding box.  The x direction considered
    "left" to "right" and the y direction is considered "bottom" to
    "top" when we thing of both geospatial and tile-centric
    coordinates.

    Note that quadkey indices are defined like this for each
    tile's children::

        ---------
        | 0 | 1 |
        --------
        | 2 | 3 |
        ---------

    The origin of a tile (row, column) is the top left of the
    bounds like Google, Bing, etc do.

    Attributes:
        bounds: The bounding box for the projection that the tiling
                scheme is defined for.
    """
    def __init__(self, xmin, ymin, xmax, ymax):
        """Constructs an object that generates tile bounds for you.

        BasicTilingTopLeft(-180, -90, 180, 270) would give you a
        square tiling scheme defined over those bounds.  Note that if
        we think of long/lat, we are covering the earth twice with
        such a scheme!

        Args:
            xmin: Minimum geospatial extent in the x direction of
                  tiling scheme.
            ymin: Minimum geospatial extent in the y direction of
                  tiling scheme.
            xmax: Maximum geospatial extent in the x direction of
                  tiling scheme.
            ymax: Maximum geospatial extent in the y direction of
                  tiling scheme.
        """
        if xmax <= xmin:
            raise ValueError("xmax must be greater than xmin")
        if ymax <= ymin:
            raise ValueError("ymax must be greater than ymin")

        # Sometimes, the public bounds aren't the same as the
        # functional ones, as in the case of the dg tiling scheme.
        self._bounds = CoordsBbox(float(xmin), float(ymin),
                                  float(xmax), float(ymax))
        self.bounds = CoordsBbox(float(xmin), float(ymin),
                                 float(xmax), float(ymax))

    def tile(self, xcoord, ycoord, zoom):
        """Returns the (x, y, z) tile at the given zoom level that
        contains the input coordinates.

        Args:
            xcoord: x direction geospatial coordinate within the tile
                    we want.
            ycoord: y direction geospatial coordinate within the tile
                    we want.
            zoom: zoom level of the tile we want.

        Returns:
            A Tile object that covers the given coordinates at the
            provided zoom level.
        """
        return Tile(x=self._x(xcoord, zoom),
                    y=self._y(ycoord, zoom),
                    z=zoom)


    def parent(self, *tile):
        """Returns the parent of the (x, y, z) tile.

        Args:
            *tile: (x, y, z) tile coordinates or a Tile object we want
                   the parent of.

        Returns:
            A Tile object representing the parent of the input.
        """
        if len(tile) == 1: # Handle if a Tile object was inputted.
            tile = tile[0]
        x, y, z = tile

        if x % 2 == 0 and y % 2 == 0: # x and y even
            return Tile(x//2, y//2, z - 1)
        elif x % 2 == 0: # x even, y odd
            return Tile(x//2, (y - 1)//2, z - 1)
        elif y % 2 == 0: # x odd, y even
            return Tile((x - 1)//2, y//2, z - 1)
        else: # x odd, y odd
            return Tile((x - 1)//2, (y - 1)//2, z - 1)


    def children(self, *tile):
        """Returns the children of the (x, y, z) tile.

        Args:
            *tile: (x, y, z) tile coordinates or a Tile object we want
                   the children of.

        Yields:
            An iterable of Tile objects representing the children of
            this tile.
        """
        if len(tile) == 1: # Handle if a Tile object was inputted.
            tile = tile[0]
        x, y, z  = tile

        return [Tile(2*x, 2*y, z + 1),
                Tile(2*x + 1, 2*y, z + 1),
                Tile(2*x, 2*y + 1, z + 1),
                Tile(2*x + 1, 2*y + 1, z + 1)]


    def ul(self, *tile):
        """Returns the upper left coordinate of the (x, y, z) tile.

        Args:
            *tile: (x, y, z) tile coordinates or a Tile object we want
                   the upper left geospatial coordinates of.

        Returns:
            The upper left geospatial coordiantes of the input tile.
        """
        if len(tile) == 1: # Handle if a Tile object was inputted.
            tile = tile[0]
        x, y, z  = tile

        return Coords(self._xcoord(x, z), self._ycoord(y, z))


    def br(self, *tile):
        """Returns the bottom right coordinate of the (x, y, z) tile.

        Args:
            *tile: (x, y, z) tile coordinates or a Tile object we want
                   the bottom right geospatial coordinates of.

        Returns:
            The bottom right geospatial coordiantes of the input tile.
        """
        if len(tile) == 1: # Handle if a Tile object was inputted.
            tile = tile[0]
        x, y, z  = tile

        return Coords(self._xcoord(x + 1, z),
                      self._ycoord(y + 1, z))


    def bbox(self, *tile):
        """Returns the bounding box of the (x, y, z) tile.

        Args:
            *tile: A tuple of (x, y, z) tile coordinates or a Tile
                   object we want the bounding box of.

        Returns:
            The bounding box of the input tile.
        """
        if len(tile) == 1: # Handle if a Tile object was inputted.
            tile = tile[0]
        x, y, z  = tile

        west, north = self.ul(tile)
        east, south = self.br(tile)
        return CoordsBbox(west, south, east, north)


    def quadkey(self, *tile):
        """Returns the quadkey of the (x, y, z) tile.

        Args:
            *tile: A tuple of (x, y, z) tile coordinates or a Tile
                   object we want the quadkey of.

        Returns:
            The quadkey of the input tile.
        """
        if len(tile) == 1: # Handle if a Tile object was inputted.
            tile = tile[0]
        x, y, z  = [int(i) for i in tile]

        quadkey = []
        for zoom in range(z, 0, -1):
            digit = 0
            mask = 1 << (zoom - 1)
            if int(x) & mask:
                digit += 1
            if int(y) & mask:
                digit += 2
            quadkey.append(digit)
        return ''.join(str(d) for d in quadkey)


    def quadkey_to_tile(self, qk):
        """Returns the Tile object represented by the input quadkey.

        Args:
            qk: A string representing the quadkey.

        Returns:
            The Tile object represented by the input quadkey.
        """
        if not qk_regex.match(qk):
            raise ValueError("Input quadkey is invalid.")

        x = 0
        y = 0
        for i, digit in enumerate(reversed(qk)):
            mask = 1 << i
            if digit == '1':
                x = x | mask
            elif digit == '2':
                y = y | mask
            elif digit == '3':
                x = x | mask
                y = y | mask
        return Tile(x, y, len(qk))

    def _xcoord(self, x, z):
        """Left geospatial coordinate of tile at given column and zoom.

        Args:
            x: The tile's column coordinate.
            z: The zoom level.

        Returns:
            The left geospatial coordinate of this tile.
        """
        return ((x/(2.**z)*(self._bounds.xmax - self._bounds.xmin)) + self._bounds.xmin)


    def _ycoord(self, y, z):
        """Top geospatial coordinate of tile at given row and zoom.

        Args:
            y: The tile's row coordinate.
            z: The zoom level.

        Returns:
            The bottom geospatial coordinate of this tile.
        """

        return (self._bounds.ymax - (y/(2.**z)*(self._bounds.ymax - self._bounds.ymin)))


    def _x(self, xcoord, zoom):
        """Get the x coordinate (column) of this tile at this zoom level.

        Args:
            xcoord: x coordinate to covert to tile index.
            zoom: zoom level of th tile we want.

        Returns:
            The x coordinate (column) of the tile.
        """
        return int(floor((2.**zoom)*(xcoord - self._bounds.xmin)/(self._bounds.xmax - self._bounds.xmin)))


    def _y(self, ycoord, zoom):
        """Get the y coordinate (row) of this tile at this zoom level.

        Note that this function assumes that the origin is on the
        top, not the bottom!

        Args:
            ycoord: y coordinate to covert to tile index.
            zoom: zoom level of th tile we want.

        Returns:
            The y coordinate (row) of the tile.
        """
        return int(floor((2.**zoom)*(self._bounds.ymax - ycoord)/(self._bounds.ymax - self._bounds.ymin)))



class DGTiling(BasicTilingBottomLeft):
    """Tiler for the DG tiling scheme.

    The DG tiling scheme is a subdivision of the WGS84 ellipsoid.
    Long/lat coordinates are directly mapped to the rectange [-180,
    180] and [-90, 90] in this scheme.  In practice, level 0 is a
    square whose latitude goes from -90 to 270, so half of this square
    is undefined!  Because of this, the tiling really starts at level
    0, with the bottom two tiles being valid.  The children method
    handles this oddity for you.
    """
    def __init__(self):
        """Construct a DG tiling scheme object for you.

        Returns:
            Tiling object that functions as the usual DG tiling scheme.
        """
        super(DGTiling, self).__init__(-180, -90, 180, 270)
        self.bounds = CoordsBbox(-180., -90., 180., 90.)

    def children(self, *tile):
        """Returns the children of the (x, y, z) tile.

        For DGTiling, note that level 0 only returns two tiles because
        the level 0 tile is twice the size of the map!

        Args:
            *tile: (x, y, z) tile coordinates or a Tile object we want
                   the children of.

        Yields:
            An iterable of Tile objects representing the children of
            this tile.
        """
        if len(tile) == 1: # Handle if a Tile object was inputted.
            tile = tile[0]
        x, y, z  = tile

        # DGTiling is weird at level zero, so deal with it.
        if z == 0:
            return [Tile(0, 0, 1), Tile(1, 0, 1)]
        return super(DGTiling, self).children(x, y, z)


class WebMercatorBL(BasicTilingBottomLeft):
    """Tile scheme for Web Mercator with the tile origin in the bottom
    left corner.

    Web Mercator (EPSG 3857) is commonly used in online mapping
    applications.  This scheme has the tile coordinates originating in
    the bottom left, which is what the `TMS specification
    <http://wiki.osgeo.org/wiki/Tile_Map_Service_Specification#TileMap_Diagram>`_
    calls for (as opposed to what Google, Bing, slippy maps, etc do).

    Note that quadkey indices are defined like this for each
    tile's children (as the Bing scheme labels them)::

        ---------
        | 0 | 1 |
        --------
        | 2 | 3 |
        ---------
    """
    def __init__(self):
        """Construct a Web Mercator tiling scheme object for you where
        the origin is in the bottom left corner.

        Returns:
            Tiling object for web mercator, with tile origin in the
            bottom left corner.
        """
        super(WebMercatorBL, self).__init__(-20037508.342789244,
                                            -20037508.342789244,
                                            20037508.342789244,
                                            20037508.342789244)

    def quadkey(self, *tile):
        """Returns the quadkey of the (x, y, z) tile.

        Args:
            *tile: A tuple of (x, y, z) tile coordinates or a Tile
                   object we want the quadkey of.

        Returns:
            The quadkey of the input tile.
        """
        if len(tile) == 1: # Handle if a Tile object was inputted.
            tile = tile[0]
        x, y, z  = [int(i) for i in tile]

        quadkey = []
        for zoom in range(z, 0, -1):
            digit = 0
            mask = 1 << (zoom - 1)
            if int(x) & mask:
                digit += 1
            if not (int(y) & mask):
                digit += 2
            quadkey.append(digit)
        return ''.join(str(d) for d in quadkey)


    def quadkey_to_tile(self, qk):
        """Returns the Tile object represented by the input quadkey.

        Args:
            qk: A string representing the quadkey.

        Returns:
            The Tile object represented by the input quadkey.
        """
        if not qk_regex.match(qk):
            raise ValueError("Input quadkey is invalid.")

        x = 0
        y = 0
        for i, digit in enumerate(reversed(qk)):
            mask = 1 << i
            if digit == '1':
                x = x | mask
            elif digit == '2':
                y = y | mask
            elif digit == '3':
                x = x | mask
                y = y | mask

        return Tile(x, 2**len(qk) - y - 1, len(qk))


class WebMercator(BasicTilingTopLeft):
    """Tile scheme for Web Mercator with the tile origin in the top
    left corner.

    Web Mercator (EPSG 3857) is commonly used in online mapping
    applications.  This scheme has the tile coordinates originating in
    the top left, which is what Google, Bing, and most others do for
    Web Mercator.

    Note that quadkey indices are defined like this for each
    tile's children (as the Bing scheme labels them)::

        ---------
        | 0 | 1 |
        --------
        | 2 | 3 |
        ---------
    """
    def __init__(self):
        """Construct a Web Mercator tiling scheme object for you where
        the origin is in the top left corner.

        Returns:
            Tiling object for web mercator, with tile origin in the
            top left corner.
        """
        super(WebMercator, self).__init__(-20037508.342789244,
                                          -20037508.342789244,
                                          20037508.342789244,
                                          20037508.342789244)


class UTMTiling(BasicTilingTopLeft):
    """A tiling of a UTM projection.

    We are building a hierarchical grid valid for a UTM projection.
    Recall that such a projection is roughtly 1,000,000 meters across
    and 20,000,000 meters tall (inclusive of both north and south
    zones) , so given a desired tile size, we build out our grid to
    cover these bounds.

    Attributes:
        zoom: The zoom level of the hierarchical grid that corresponds
              to the user provided tile_size.

    """
    def __init__(self, tile_size):
        """Constructs a UTMTiling object.

        Args:
            tile_size: The size of the tile grid (meters) you want to
                       use as a covering of the UTM bounds.
                       E.G. 100_000 would correspond to the 100km MGRS
                       tiling for this zone.

        Returns:
            A tiling object valid for a UTM projection.
        """
        if tile_size <= 0.0:
            raise ValueError('tile_size must be positive')
        self.tile_size = tile_size

        # For this tile size, figure out the size of the bounding box
        # that covers the UTM projection bounds. Remember that a UTM
        # zone is 10_000_000 meters tall as measured from the origin
        # so we need to have a map size that exceeds that dimension.
        zoom = ceil(log2(10_000_000.0/self.tile_size))
        map_size = self.tile_size * 2**zoom
        self.zoom = zoom + 1

        super().__init__(-map_size + 500_000.0, -map_size,
                          map_size + 500_000.0,  map_size)



class WorldNorthernUTMTiling(UTMTiling):
    """
    Transforms Southern Hemisphere Polar axes coordinates onto
    the Northern Hemisphere Polar axes, which defines the origin
    towards the Southern Pole and the positive upper bound to the North.
    Amounts to a simple translation by the UTM zone height.

    Convenience subclass that modifies the two public methods
    used by the other geographic methods so as to make the change
    at the source where the use case is relevant.
    """

    def ul(self, *tile):
        """Returns the upper left coordinate of the (x, y, z) tile, and
        translates the y coordinate to UTM Northern Hemisphere South-North
        bounds if the tile is defined by UTM Southern Hemisphere bounds.

        Args:
            *tile: (x, y, z) tile coordinates or a Tile object we want
                   the upper left geospatial coordinates of.
        Returns:
            The upper left geospatial coordiantes of the input tile.
        """

        coords = super().ul(*tile)
        if self.quadkey(*tile)[0] in ('2', '3'):
            coords = Coords(coords.x, coords.y + 10_000_000)
        return coords

    def br(self, *tile):
        """Returns the bottom right coordinate of the (x, y, z) tile, and
        translates the y coordinate to UTM Northern Hemisphere South-North
        bounds if the tile is defined by UTM Southern Hemisphere bounds.

        Args:
            *tile: (x, y, z) tile coordinates or a Tile object we want
                   the bottom right geospatial coordinates of.
        Returns:
            The bottom right geospatial coordiantes of the input tile.
        """


        coords = super().br(*tile)
        if self.quadkey(*tile)[0] in ('2', '3'):
            coords = Coords(coords.x, coords.y + 10_000_000)
        return coords



class UTM5kmTiling(UTMTiling):
    """A 5km tiling of a UTM zone.

    Note that the zoom attribute tells you what zoom level corresponds
    to the 5km tiles.
    """
    def __init__(self):
        super().__init__(5_000)


class UTM10kmTiling(UTMTiling):
    """A 10km tiling of a UTM zone.

    Note that the zoom attribute tells you what zoom level corresponds
    to the 10km tiles.
    """
    def __init__(self):
        super().__init__(10_000)


class UTM100kmTiling(UTMTiling):
    """A 100km tiling of a UTM zone.

    Note that the zoom attribute tells you what zoom level corresponds
    to the 100km tiles.
    """
    def __init__(self):
        super().__init__(100_000)


class WNUTM5kTiling(UTM5kmTiling, WorldNorthernUTMTiling):
    pass


class WNUTM10kmTiling(UTM10kmTiling, WorldNorthernUTMTiling):
    pass


class WNUTM100kmTiling(UTM100kmTiling, WorldNorthernUTMTiling):
    pass






