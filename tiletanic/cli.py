#TODO:
# Add click tests
# Add documentation - how to run with a file vs stdout, document arguments, etc.
import click
import geojson
from shapely import geometry, ops, prepared
import fiona
import tiletanic

@click.group()
@click.version_option()
def cli():
    """CLI entry point for tiletanic"""
    pass

@cli.command()
@click.option('--hemisphere', type=click.Choice('N', 'S'),
              default='N',
              help='the north or south hemisphere')
@click.option('--driver', default='GPKG',
              help='GDAL driver to use for output file')
@click.argument('tile_size', type=click.IntRange(1,))
@click.argument('zone', type=click.IntRange(1, 60))
@click.argument('f_out', type=click.Path())
def utmgrid(hemisphere, tile_size, driver, zone, f_out):
    scheme = tiletanic.tileschemes.UTMTiling(tile_size)
    
    minx, miny, maxx, maxy = 0.0, 0.0, 0.0, 0.0
    if hemisphere == 'S':
        miny += 10_000_000
        maxy += 10_000_000
        epsg_utm_code = 'EPSG:327{:02d}'.format(zone)
    else:
        epsg_utm_code = 'EPSG:326{:02d}'.format(zone)

    with fiona.open(f_out, 'w', driver=driver, crs=epsg_utm_code,
                    schema={'geometry': 'Polygon',
                            'properties':{'tileID':'str'}}) as sink:
        
        for t in scheme.grid():
            g = geometry.mapping(geometry.box(*[c1+c2 for c1, c2 in zip(scheme.bbox(t), (minx, miny, maxx, maxy))]))
            sink.write({
                'geometry': g,
                'properties':{
                    'tileID': 'Z{:02d}-{}'.format(zone, scheme.quadkey(t))
                },
            })
            
    

@cli.command()
@click.option('--zoom', default=9, type=click.IntRange(0,26),
              help="Zoom level at which to generate tile covering of "
                   "AOI_GEOJSON.  Default=9")
@click.option('--adjacent/--no-adjacent', default = False,
              help="Include all tiles that have at least one boundary "
                    "point in common, but not necessarily interior "
                    "points. Default=do not include adjacent tiles")
@click.argument('aoi_geojson', type=click.File('r'))
def dgqks(zoom, adjacent, aoi_geojson):
    """Calculate a tile covering for an input AOI_GEOJSON at a particular
    ZOOM level using the DigitalGlobe tilescheme.

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
    scheme = tiletanic.tileschemes.DGTiling()
    aoi = geojson.loads( aoi_geojson.read() )

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
