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
    tiles = [tile for tile in cover_geometry(tiler, geometry.Point(-94.39453125, 15.908203125), 12)]
    assert len(tiles) == 1
