"""Common data structures for Tiletanic."""
from math import floor
from collections import namedtuple

from shapely import geometry

Tile = namedtuple('Tile', ['x', 'y', 'z'])
Coords = namedtuple('Coords', ['x', 'y'])
CoordsBbox = namedtuple('CoordsBbox', ['xmin', 'ymin', 'xmax', 'ymax'])

class BaseTiling(object):

    def __init__(self, xmin, ymin, xmax, ymax):
        """Constructs an object that generates tile bounds for you.

        :param xmin: minimum extent in the x range of tiling scheme.

        """
        if xmax <= xmin:
            raise ValueError("xmax must be greater than xmin")
        if ymax <= ymin:
            raise ValueError("ymax must be greater than ymin")

        self.bounds = CoordsBbox(float(xmin), float(ymin), float(xmax), float(ymax))


    def tile(self, xcoord, ycoord, zoom):
        """Returns the (x,y,z) tile at the given zoom level that
        contains the input coordinates.

        :param xcoord: x coordinate within the tile we want.
        :param ycoord: y coordinate within the tile we want.
        :param zoom: zoom level of the tile we want.
        """
        return Tile(x=self.x(xcoord, zoom),
                    y=self.y(ycoord, zoom),
                    z=zoom)
        

    def x(self, xcoord, zoom):
        """X coordinate and zoo to x tile index.

        :param xcoord: x coordinate to covert to tile index.
        :param zoom: zoom level of th tile we want.
        """
        return int(floor((2.**zoom)*(xcoord - self.bounds.xmin)/(self.bounds.xmax - self.bounds.xmin)))


    def y(self, ycoord, zoom):
        """X coordinate and zoo to x tile index.

        :param ycoord: y coordinate to covert to tile index.
        :param zoom: zoom level of th tile we want.
        """

        return int(floor((2.**zoom)*(ycoord - self.bounds.ymin)/(self.bounds.ymax - self.bounds.ymin)))


