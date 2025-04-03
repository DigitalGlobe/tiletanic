#TODO:
# Add click tests
# Add documentation - how to run with a file vs stdout, document arguments, etc.

import click
import json
from shapely import geometry, ops, prepared
import tiletanic

@click.group()
@click.version_option()
def cli():
    """CLI entry point for tiletanic"""
    pass

@cli.command()
@click.option('--tilescheme', default="DGTiling",
              type=click.Choice(['DGTiling']),
              help="DGTiling is the only supported Tiling Scheme at "
                   "this time.")
@click.argument('aoi_geojson', type=click.File('r'))
@click.option('--zoom', default=9, type=click.IntRange(0,26),
              help="Zoom level at which to generate tile covering of "
                   "AOI_GEOJSON.  Default=9")
@click.option('--adjacent/--no-adjacent', default = False,
              help="Include all tiles that have at least one boundary "
                    "point in common, but not necessarily interior "
                    "points. Default=do not include adjacent tiles")
@click.option('--quadkey/--no-quadkey', default=True,
              help="Output option to prints the quadkeys of the tile "
                   "covering generated. Default prints quadkeys")
def cover_geometry(tilescheme, aoi_geojson, zoom, adjacent, quadkey):
    """Calculate a tile covering for an input AOI_GEOJSON at a particular
    ZOOM level using the given TILESCHEME.

    AOI_GEOJSON - Area of Interest which needs to be chopped into a
    tile covering encoded as GeoJSON.  Should be either a single
    Feature or a FeatureCollection.  Read in from positional argument
    or stdin.

    Example with geojson file input:

    \b
        $ tiletanic cover_geometry aoi.geojson
        021323330

    Example with stdin input:

    \b
        $ cat << EOF | tiletanic cover_geometry -
        > {
        >     "geometry": {
        >         "coordinates": [
        >             [
        >                 [ -101.953125, 43.59375],
        >                 [ -101.953125, 44.296875],
        >                 [ -102.65625,  44.296875],
        >                 [ -102.65625,  43.59375],
        >                 [ -101.953125, 43.59375]
        >             ]
        >         ],
        >         "type": "Polygon"
        >     },
        >     "properties": {},
        >     "type": "Feature"
        > }
        > EOF
        021323330

    """

    if tilescheme == 'DGTiling':
        scheme = tiletanic.tileschemes.DGTiling()
    else:
        raise ValueError("tilescheme '{}' is unsupported.").format(tilescheme)

    aoi = json.loads( aoi_geojson.read() )

    if 'type' not in aoi:
        raise ValueError("The 'AOI_GEOJSON' doesn't have a 'type' member. Is it valid GeoJSON?")
    elif aoi['type'] == 'FeatureCollection':
        geom = ops.unary_union([geometry.shape(f['geometry'])
                                for f in aoi['features']
                                if f['geometry']['type'].endswith('Polygon')])
    elif aoi['type'] == 'Feature':
        geom = geometry.shape(aoi['geometry'])
    else:
        raise ValueError("The AOI_GEOJSON 'type' %s is unsupported, " % aoi['type'] +
                         "it must be 'Feature' or 'FeatureCollection'")

    tiles = tiletanic.tilecover.cover_geometry(scheme, geom, zoom)

    if not adjacent:
        tiles = _tiles_inside_geom(scheme, tiles, geom)

    if quadkey:
        qks = [scheme.quadkey(t) for t in tiles]
        click.echo( "\n".join( qks ) )


def _tiles_inside_geom(tilescheme, tiles, geom):
    """Filters out tiles do not contain the geometry geom

    Consider the nine adjacent tiles:

       -------------
       | 1 | 2 | 3 |
       -------------
       | 4 | 5 | 6 |
       -------------
       | 7 | 8 | 9 |
       -------------

    if the AOI is 5, _tiles_inside_geom will only return 5.  Note that
    tiletanic.tilecover.cover_geometry returns all 9 tiles

    Args:
      tilescheme: The tile scheme to use.
      tiles: list iterable collection of tiles
      geom: Shapely Geometry area of interest
    """
    prep_geom = prepared.prep(geom)
    for t in tiles:
        coords = tilescheme.bbox(t)
        tile_geom = geometry.Polygon(((coords.xmin, coords.ymin),
                                      (coords.xmax, coords.ymin),
                                      (coords.xmax, coords.ymax),
                                      (coords.xmin, coords.ymax),
                                      (coords.xmin, coords.ymin)))

        # Touches: The Geometries have at least one boundary point in
        # common, but no interior points
        if not prep_geom.touches(tile_geom):
            yield t
