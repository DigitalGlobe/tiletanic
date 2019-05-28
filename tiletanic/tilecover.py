from collections import Iterable

from shapely import geometry, ops, prepared

from .base import Tile


def cover_geometry(tilescheme, geom, zooms):
    """Covers the provided geometry with tiles.

    Args:
        tilescheme: The tile scheme to use.  This needs to implement
                    the public protocal of the schemes defined within
                    tiletanic.
        geom: The geometry we would like to cover.  This should be a
              shapely geometry.
        zooms: The zoom levels of the tiles to cover geom with.  If
               you provide an iterable of zoom levels, you'll get the
               biggest tiles available that cover the geometry at
               those levels.

    Yields:
        An iterator of Tile objects ((x, y, z) named tuples) that
        cover the input geometry.
    """
    # Only shapely geometries allowed.
    if not isinstance(geom, geometry.base.BaseGeometry):
        raise ValueError("Input 'geom' is not a known shapely geometry type")

    if geom.is_empty:
        return

    zooms = zooms if isinstance(zooms, Iterable) else [zooms]

    # Generate the covering.
    prep_geom = prepared.prep(geom)    
    if isinstance(geom, (geometry.Polygon, geometry.MultiPolygon)):        
        for tile in _cover_polygonal(tilescheme, Tile(0, 0, 0), prep_geom, geom, zooms):
            yield tile
    else:
        for tile in _cover_geometry(tilescheme, Tile(0, 0, 0), prep_geom, geom, zooms):
            yield tile


def _cover_geometry(tilescheme, curr_tile, prep_geom, geom, zooms):
    """Covers geometries with tiles by recursion. 

    Args:
        tilescheme: The tile scheme to use.  This needs to implement
                    the public protocal of the schemes defined within
                    tiletanic.
        curr_tile: The current tile in the recursion scheme.
        prep_geom: The prepared version of the geometry we would like to cover.  
        geom: The shapely geometry we would like to cover.          
        zooms: The zoom levels to recurse to.

    Yields:
        An iterator of Tile objects ((x, y, z) tuples) that
        cover the input geometry.
    """
    if prep_geom.intersects(geometry.box(*tilescheme.bbox(curr_tile))):
        if curr_tile.z in zooms:
            yield curr_tile
        else:
            for tile in (tile for child_tile in tilescheme.children(curr_tile)
                         for tile in _cover_geometry(tilescheme, child_tile,
                                                     prep_geom, geom,
                                                     zooms)):
                yield tile


def _cover_polygonal(tilescheme, curr_tile, prep_geom, geom, zooms):
    """Covers polygonal geometries with tiles by recursion. 

    This is method is slightly more efficient than _cover_geometry in
    that we can check if a tile is completely covered by a geometry
    and if so, skip directly to the max zoom level to fetch the
    covered tiles.

    Args:
        tilescheme: The tile scheme to use.  This needs to implement
                    the public protocal of the schemes defined within
                    tiletanic.
        curr_tile: The current tile in the recursion scheme.
        prep_geom: The prepared version of the polygonal geometry we
                   would like to cover. 
        geom: The shapely polygonal geometry we would like to cover.          
        zooms: The zoom levels to recurse to.

    Yields:
        An iterator of Tile objects ((x, y, z) tuples) that
        cover the input polygonal geometry.
    """
    tile_geom = geometry.box(*tilescheme.bbox(curr_tile))
    if prep_geom.intersects(tile_geom):
        if curr_tile.z == max(zooms):
            yield curr_tile
        elif prep_geom.contains(tile_geom):
            if curr_tile.z in zooms:
                yield curr_tile
            else:
                for tile in (tile for child_tile in tilescheme.children(curr_tile)
                             for tile in _containing_tiles(tilescheme, child_tile, zooms)):
                    yield tile
        else:
            tiles = []
            coverage = 0
            for tile in (tile for child_tile in tilescheme.children(curr_tile)
                         for tile in _cover_polygonal(tilescheme, child_tile,
                                                      prep_geom, geom, zooms)):
                if curr_tile.z in zooms:
                    tiles.append(tile)
                    coverage += 4 ** (max(zooms) - tile.z)
                else:
                    yield tile

            if curr_tile.z in zooms and coverage == 4 ** (max(zooms) - curr_tile.z):
                yield curr_tile
            else:
                for tile in tiles:
                    yield tile


def _containing_tiles(tilescheme, curr_tile, zooms):
    """Given a Tile, returns the tiles that compose that tile at the
    zoom level provided.

    Args:
        tilescheme: The tile scheme to use.  This needs to implement
                    the public protocal of the schemes defined within
                    tiletanic.
        curr_tile: The current tile in the recursion scheme.
        zooms: The zoom levels to recurse to.

    Yields:
        An iterator of Tile objects ((x, y, z) tuples) that
        compose the input tile.
    """
    if curr_tile.z in zooms:
        yield curr_tile
    else:
        for tile in (tile for child_tile in tilescheme.children(curr_tile)
                     for tile in _containing_tiles(tilescheme, child_tile, zooms)):
            yield tile
