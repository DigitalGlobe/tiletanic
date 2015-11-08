import geojson

from shapely import geometry

def tiles_to_geojson(tiles, tilescheme, crs=None):
    """Return the collection of Tile objects as a GeoJSON feature
    collection.  """
    gen = (geometry.box(*tilescheme.bbox(tile)) for tile in tiles)
    gen = (geometry.mapping(box) for box in gen)
    gen = (geojson.Feature(geometry=mapping) for mapping in gen)
    return geojson.dumps(geojson.FeatureCollection(features=[f for f in gen], crs=crs))
        
