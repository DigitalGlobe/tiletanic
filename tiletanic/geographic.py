from math import floor
import re

from base import Tile, Coords, CoordsBbox

qk_regex = re.compile(r'[0-3]+$')

class GeographicTiling(object):
    """GeographicTiling is a class for representing a tiling scheme
    defined in the projection EPSG:4326, commonly refered to as
    geographic or unprojected.  
    """
    def __init__(self, xmin, ymin, xmax, ymax):
        """Constructs an object that generates tile bounds for you.

        GeographicTiling(-180, -90, 180, 270) would to the DG tiling
        scheme.
        
        Args:
            xmin: minimum extent in the x range of tiling scheme.
        """
        if xmax <= xmin:
            raise ValueError("xmax must be greater than xmin")
        if ymax <= ymin:
            raise ValueError("ymax must be greater than ymin")

        self.bounds = CoordsBbox(float(xmin), float(ymin),
                                 float(xmax), float(ymax))

    @classmethod
    def dgtiling(cls):
        """Returns this class instantiated as the DG tiling scheme.

        The DG tiling scheme is a subdivision of the WGS84 ellipsoid.
        Long/lat coordinates are directly mapped to the rectange
        [-180, 180] and [-90, 90] in this scheme.  In practice, level
        0 is a square whose latitude goes from -90 to 270, so half of
        this square is undefined!  Because of this, the tiling really
        starts at level 0, with the bottom two tiles being valid.
        Note that quadkey indices are defined like this for each
        square:

        ---------
        | 2 | 3 |
        ---------
        | 0 | 1 |
        ---------

        The origin of a tile (row, column) is the bottom left of the
        bounds, as opposed to some of the web mercator schemes!

        Returns:
            Tiling object that functions as the usual DG tiling scheme.
        """
        return cls(-180, -90, 180, 270)


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
            tile: A tuple of (x, y, z) tile coordinates or a Tile
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
            tile: A tuple of (x, y, z) tile coordinates or a Tile
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
        return ((x/(2.**z)*(self.bounds.xmax - self.bounds.xmin)) + self.bounds.xmin)


    def _ycoord(self, y, z):
        """Bottom geospatial coordinate of tile at given row and zoom.

        Args:
            y: The tile's row coordinate.
            z: The zoom level.

        Returns:
            The bottom geospatial coordinate of this tile.
        """

        return ((y/(2.**z)*(self.bounds.ymax - self.bounds.ymin)) + self.bounds.ymin)

    
    def _x(self, xcoord, zoom):
        """Get the x coordinate (column) of this tile at this zoom level.

        Args:
            xcoord: x coordinate to covert to tile index.
            zoom: zoom level of th tile we want.

        Returns:
            The x coordinate (column) of the tile.
        """
        return int(floor((2.**zoom)*(xcoord - self.bounds.xmin)/(self.bounds.xmax - self.bounds.xmin)))


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
        return int(floor((2.**zoom)*(ycoord - self.bounds.ymin)/(self.bounds.ymax - self.bounds.ymin)))


