import geojson

from shapely import geometry

def tiles_to_geojson(tiles, tilescheme):

    gen = (geometry.box(*tilescheme.bbox(tile)) for tile in tiles)
    gen = (geometry.mapping(box) for box in gen)
    gen = (geojson.Feature(geometry=mapping) for mapping in gen)
    return geojson.dumps(geojson.FeatureCollection(features=[f for f in gen]))
        
