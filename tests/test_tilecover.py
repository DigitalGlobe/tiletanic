import pytest
from shapely import geometry

from tiletanic.tilecover import cover_geometry
from tiletanic.tileschemes import DGTiling

@pytest.fixture
def tiler():
    return DGTiling()


def test_cover_geometry_empty_geoms(tiler):
    """Empty geometries should return empty iterators."""
    assert not cover_geometry(tiler, geometry.Point(), 0) == True
    assert not cover_geometry(tiler, geometry.MultiPoint(), 0) == True
    assert not cover_geometry(tiler, geometry.LineString(), 0) == True
    assert not cover_geometry(tiler, geometry.MultiLineString(), 0) == True
    assert not cover_geometry(tiler, geometry.Polygon(), 0) == True
    assert not cover_geometry(tiler, geometry.MultiPolygon(), 0) == True
    assert not cover_geometry(tiler, geometry.GeometryCollection(), 0) == True


def test_cover_geometry_nonshapely_geom(tiler):
    """Only accept shapely geometries."""
    with pytest.raises(ValueError):
        for tile in cover_geometry(tiler, None, 0):
            pass

        
def test_cover_geometry_single_point(tiler):
    """A Point geometry."""
    pt = geometry.Point(-94.39453125, 15.908203125)
    
    # Should only get one tile back at level 4.
    tiles = [tile for tile in cover_geometry(tiler, pt, 4)]
    assert len(tiles) == 1
    assert set(tiles) == {(3, 4, 4)}

    # Four tiles should come back for this point at level 12 as it lies on a corner.
    tiles = [tile for tile in cover_geometry(tiler, pt, 12)]
    assert len(tiles) == 4
    assert set(tiles) == {(973, 1204, 12), (973, 1205, 12), (974, 1204, 12), (974, 1205, 12)}


def test_cover_geometry_multi_point(tiler):
    """A MultiPoint geometry."""    
    mp = geometry.MultiPoint([(-94.39453125, 15.908203125),
                              (-94.306640625, 15.908203125),
                              (-94.306640625, 15.8203125),
                              (-94.39453125, 15.8203125)])

    # Should only get one tile back at level 4.
    tiles = [tile for tile in cover_geometry(tiler, mp, 4)]
    assert len(tiles) == 1

    # Should get nine tiles back at level 12 for this point set.
    tiles = [tile for tile in cover_geometry(tiler, mp, 12)]
    assert len(tiles) == 9
    assert set(tiles) == {(973, 1203, 12), (974, 1203, 12), (975, 1203, 12),
                          (973, 1204, 12), (973, 1205, 12), (974, 1204, 12),
                          (975, 1204, 12), (974, 1205, 12), (975, 1205, 12)}
                          
                           
def test_cover_geometry_linestring(tiler):
    """A LineString geometry."""
    ls = geometry.shape({"coordinates": [[-123.12515258789061, 45.70809729528788], [-122.4755859375, 45.615958580368364], [-123.32977294921874, 45.44664375276733], [-122.25173950195311, 45.334771196762766], [-123.3819580078125, 45.11133093583217], [-122.23388671874999, 45.04829981381567], [-122.57995605468749, 45.74740199642105], [-122.6348876953125, 44.961882876810925], [-122.80654907226562, 45.75315158411652], [-122.98645019531249, 44.998795943614084], [-123.05648803710938, 45.744526980468436], [-123.33938598632812, 45.031803280058554]], "type": "LineString"})

    tiles = [tile for tile in cover_geometry(tiler, ls, 4)]
    assert len(tiles) == 2
    assert set(tiles) == {(2, 5, 4), (2, 6, 4)}

    tiles = [tile for tile in cover_geometry(tiler, ls, 11)]
    assert len(tiles) == 30
    assert set(tiles) == {(322, 768, 11), (322, 769, 11), (322, 770, 11), (323, 768, 11),
                          (323, 769, 11), (323, 770, 11), (323, 771, 11), (323, 772, 11),
                          (324, 767, 11), (324, 768, 11), (324, 769, 11), (324, 770, 11),
                          (324, 771, 11), (325, 768, 11), (325, 769, 11), (325, 770, 11),
                          (325, 771, 11), (325, 772, 11), (326, 767, 11), (326, 768, 11),
                          (326, 769, 11), (326, 770, 11), (326, 771, 11), (326, 772, 11),
                          (327, 768, 11), (327, 769, 11), (327, 770, 11), (327, 771, 11),
                          (328, 768, 11), (328, 769, 11)}
