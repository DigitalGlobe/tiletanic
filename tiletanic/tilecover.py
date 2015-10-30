from collections import Iterable

from shapely import geometry, ops, prepared

from .base import Tile

def cover_geometry(tilescheme, geom, zoom):
    """Covers the provided geometry with tiles.

    Args:
        tilescheme: The tile scheme to use.  This needs to implement
                    the public protocal of the schemes defined within
                    tiletanic.
        geom: The geometry we would like to cover.  This should be a
              shapely geometry.
        zoom: The zoom level of the tiles to cover geom with.

    Yields:
        An iterator of Tile objects ((x, y, z) named tuples) that
        cover the input geometry.
    """
    # Only shapely geometries allowed.
    if not isinstance(geom, geometry.base.BaseGeometry):
        raise ValueError("Input 'geom' is not a known shapely geometry type")
    
    if geom.is_empty:
        return

    # Generate the covering.
    prep_geom = prepared.prep(geom)
    for tile in _cover_geometry(tilescheme, Tile(0, 0, 0), prep_geom, geom, zoom):
        yield tile

def _cover_geometry(tilescheme, curr_tile, prep_geom, geom, max_zoom):
    """Covers geometries with tiles by recursion. 

    Args:
        tilescheme: The tile scheme to use.  This needs to implement
                    the public protocal of the schemes defined within
                    tiletanic.
        curr_tile: 
        prep_geom: The prepared version of the geometry we would like to cover.  
        geom: The shapely geometry we would like to cover.          
        max_zoom: The zoom level to recurse to.

    Yields:
        An iterator of Tile objects ((x, y, z) tuples) that
        cover the input geometry.
    """
    if prep_geom.intersects(geometry.box(*tilescheme.bbox(curr_tile))):
        if curr_tile.z == max_zoom:
            yield curr_tile
        else:
            for tile in (tile for child_tile in tilescheme.children(curr_tile)
                         for tile in _cover_geometry(tilescheme, child_tile,
                                                     prep_geom, geom, max_zoom)):
                yield tile
    
