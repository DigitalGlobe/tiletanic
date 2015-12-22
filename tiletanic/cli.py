#TODO:
# Add click tests
# Add documentation - how to run with a file vs stdout, document arguments, etc.

import click
import geojson
from shapely import geometry, ops
import tiletanic


@click.group()
@click.version_option()
def cli():
    """CLI entry point for tiletanic"""
    pass

@cli.command()
@click.option('--tilescheme', default="DGTiling", type=click.Choice(['DGTiling']))
@click.argument('aoi_geojson', type=click.File('r'))
@click.option('--zoom', default=9, type=click.IntRange(0,26))
@click.option('--quadkey', default=True)
def cover_geometry(tilescheme, aoi_geojson, zoom, quadkey):
    """Calculate a tile covering at a particular zoom level for the given AOI"""
    aoi = geojson.loads(''.join(aoi_geojson.readlines()))

    if 'type' not in aoi:
        raise ValueError("The 'aoi_geojson' doesn't have a 'type' member. Is it valid GeoJSON?")
    elif aoi['type'] == 'FeatureCollection':
        geom = ops.unary_union([geometry.shape(f['geometry'])
                                for f in aoi['features']
                                if f['geometry']['type'].endswith('Polygon')])
    elif aoi['type'] == 'Feature':
        geom = geometry.shape(aoi['geometry'])
    else:
        raise ValueError("The aoi 'type' %s is unsupported, " % aoi['type'] +
                         "it must be 'Feature' or 'FeatureCollection'")

    if tilescheme == 'DGTiling':
        scheme = tiletanic.tileschemes.DGTiling()

    tiles = tiletanic.tilecover.cover_geometry(scheme, geom, zoom)

    if quadkey:
        qks = [scheme.quadkey(t) for t in tiles]
        click.echo( "\n".join( qks ) )
