"""Common data structures for Tiletanic."""
from collections import namedtuple

Tile = namedtuple('Tile', ['x', 'y', 'z'])
Coords = namedtuple('Coords', ['x', 'y'])
CoordsBbox = namedtuple('CoordsBbox', ['xmin', 'ymin', 'xmax', 'ymax'])

