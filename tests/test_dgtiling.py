import pytest

from tiletanic.tileschemes import DGTiling

@pytest.fixture
def tiler():
    return DGTiling()


def test_bounds(tiler):
    """Geographic bounds."""
    assert tiler.bounds.xmin == -180.
    assert tiler.bounds.xmax == 180.
    assert tiler.bounds.ymin == -90.
    assert tiler.bounds.ymax == 90.

    
def test_tile(tiler):
    """Tile generation from gespatial coordinates and zoom."""
    assert tiler.tile(0., 0., 0) == (0, 0, 0)

    assert tiler.tile(-90., 0., 1) == (0, 0, 1)
    assert tiler.tile(90., 0., 1) == (1, 0, 1)

    assert tiler.tile(-135., -45., 2) == (0, 0, 2)
    assert tiler.tile(-45., -45., 2) == (1, 0, 2)
    assert tiler.tile(45., -45., 2) == (2, 0, 2)
    assert tiler.tile(135., -45., 2) == (3, 0, 2)
    assert tiler.tile(-135., 45., 2) == (0, 1, 2)
    assert tiler.tile(-45., 45., 2) == (1, 1, 2)
    assert tiler.tile(45., 45., 2) == (2, 1, 2)
    assert tiler.tile(135., 45., 2) == (3, 1, 2)
    
    assert tiler.tile(105.1092, 40.1717, 12) == (3243, 1481, 12)


def test_parent(tiler):
    """Parent of a tile."""
    assert tiler.parent(0, 0, 1) == (0, 0, 0)
    assert tiler.parent(1, 0, 1) == (0, 0, 0)

    assert tiler.parent(2, 3, 2) == (1, 1, 1)
    assert tiler.parent(3, 0, 2) == (1, 0, 1)


def test_children1(tiler):
    """Children of a level 0 tile."""
    assert set(tiler.children(0, 0, 0)) == {(0, 0, 1),
                                            (1, 0, 1)}

    
def test_children2(tiler):
    """Children of a level > 0 tile."""
    assert set(tiler.children(1, 1, 1)) == {(2, 2, 2),
                                            (2, 3, 2),
                                            (3, 2, 2),
                                            (3, 3, 2)}
    

def test_quadkey(tiler):
    "Quadkey generation from tile coordinates."""
    assert tiler.quadkey(0, 0, 1) == '0'
    assert tiler.quadkey(1, 0, 1) == '1'

    assert tiler.quadkey(0, 0, 2) == '00'
    assert tiler.quadkey(1, 0, 2) == '01'
    assert tiler.quadkey(0, 1, 2) == '02'
    assert tiler.quadkey(1, 1, 2) == '03'
    assert tiler.quadkey(2, 0, 2) == '10'
    assert tiler.quadkey(3, 0, 2) == '11'
    assert tiler.quadkey(2, 1, 2) == '12'
    assert tiler.quadkey(3, 1, 2) == '13'

    assert not tiler.quadkey(0, 0, 0)

    assert tiler.quadkey(3, 1, 3) == '013'
    assert tiler.quadkey(4, 1, 3) == '102'
    assert tiler.quadkey(3, 2, 3) == '031'
    assert tiler.quadkey(4, 2, 3) == '120'

    assert tiler.quadkey(20, 35, 9) == '000210122'

        
def test_ul(tiler):
    """Upper left coordinates of input tile."""
    assert tiler.ul(0, 0, 1) == (-180., 90.)
    assert tiler.ul(1, 0, 1) == (0., 90.)
    
    assert tiler.ul(3, 1, 3) == (-45., 0.)
    assert tiler.ul(4, 1, 3) == (0., 0.)
    assert tiler.ul(3, 2, 3) == (-45., 45.)
    assert tiler.ul(4, 2, 3) == (0., 45.)
    
    
def test_br(tiler):
    """Bottom right coordinates of input tile."""
    assert tiler.br(0, 0, 1) == (0., -90.)
    assert tiler.br(1, 0, 1) == (180., -90.)
    
    assert tiler.br(3, 1, 3) == (0., -45.)
    assert tiler.br(4, 1, 3) == (45., -45.)
    assert tiler.br(3, 2, 3) == (0., 0.)
    assert tiler.br(4, 2, 3) == (45., 0.)


def test_bbox(tiler):   
    """Bounding boxes of tiles."""
    assert tiler.bbox(0, 0, 1) == (-180, -90., 0., 90.)
    assert tiler.bbox(1, 0, 1) == (0., -90., 180., 90.)
    
    assert tiler.bbox(3, 1, 3) == (-45., -45., 0., 0.)
    assert tiler.bbox(4, 1, 3) == (0., -45., 45., 0.)
    assert tiler.bbox(3, 2, 3) == (-45., 0., 0., 45.)
    assert tiler.bbox(4, 2, 3) == (0., 0., 45., 45.)

    
def test_quadkey_to_tile1(tiler):
    """Quadkey to tile exceptions."""
    with pytest.raises(ValueError):
        tiler.quadkey_to_tile('4')

    
def test_quadkey_to_tile2(tiler):
    """Quadkey to tile."""
    assert tiler.quadkey_to_tile('0') == (0, 0, 1)
    assert tiler.quadkey_to_tile('130232101') == (405, 184, 9)
