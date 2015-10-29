from collections import Iterable

from shapely import geometry, ops, prepared

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
    for tile in _cover_geometry(tilescheme, prep_geom, geom, 0, zoom):
        yield tile

def _cover_geometry(tilescheme, prep_geom, geom, this_zoom, max_zoom):
    """Covers geometries with tiles by recursion. 

    Args:
        tilescheme: The tile scheme to use.  This needs to implement
                    the public protocal of the schemes defined within
                    tiletanic.
        prep_geom: The prepared version of the geometry we would like to cover.  
        geom: The shapely geometry we would like to cover.  
        this_zoom: The current zoom level.
        max_zoom: The zoom level to recurse to.

    Yields:
        An iterator of Tile objects ((x, y, z) tuples) that
        cover the input geometry.
    """
    return []
    
