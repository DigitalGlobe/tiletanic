import pytest

from tiletanic.tileschemes import BasicTilingBottomLeft

@pytest.fixture
def tiler():
    return BasicTilingBottomLeft(0, 0, 1, 1)


def test_init():
    """Constructor exceptions."""
    with pytest.raises(ValueError):
        BasicTilingBottomLeft(1, 0, 1, 1)

    with pytest.raises(ValueError):
        BasicTilingBottomLeft(0, 1, 1, 1)
        
def test_bounds(tiler):
    """Geographic bounds."""
    assert tiler.bounds.xmin == 0.
    assert tiler.bounds.ymin == 0.
    assert tiler.bounds.xmax == 1.
    assert tiler.bounds.ymax == 1.

    
def test_tile(tiler):
    """Tile generation from gespatial coordinates and zoom."""
    assert tiler.tile(0., 0., 0) == (0, 0, 0)

    assert tiler.tile(0.25, 0.25, 1) == (0, 0, 1)
    assert tiler.tile(0.75, 0.25, 1) == (1, 0, 1)
    assert tiler.tile(0.25, 0.75, 1) == (0, 1, 1)
    assert tiler.tile(0.75, 0.75, 1) == (1, 1, 1)


def test_parent(tiler):
    """Parent of a tile."""
    assert tiler.parent(0, 0, 1) == (0, 0, 0)
    assert tiler.parent(1, 0, 1) == (0, 0, 0)

    assert tiler.parent(2, 3, 2) == (1, 1, 1)
    assert tiler.parent(3, 0, 2) == (1, 0, 1)


def test_children(tiler):
    """Children of a tile."""
    assert set(tiler.children(0, 0, 0)) == {(0, 0, 1),
                                            (0, 1, 1),
                                            (1, 0, 1),
                                            (1, 1, 1)}
    
def test_quadkey(tiler):
    """Quadkey generation from tile coordinates."""
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

    assert tiler.quadkey(20, 35, 9) == '000210122'


def test_ul(tiler):
    """Upper left coordinates of input tile."""
    assert tiler.ul(0, 0, 0) == (0., 1.)

    assert tiler.ul(0, 0, 1) == (0., 0.5)
    assert tiler.ul(1, 0, 1) == (0.5, 0.5)
    assert tiler.ul(0, 1, 1) == (0., 1.)
    assert tiler.ul(1, 1, 1) == (0.5, 1.)

    
def test_br(tiler):
    """Bottom right coordinates of input tile."""
    assert tiler.br(0, 0, 0) == (1., 0.)
    
    assert tiler.br(0, 0, 1) == (0.5, 0.)
    assert tiler.br(1, 0, 1) == (1., 0.)
    assert tiler.br(0, 1, 1) == (0.5, 0.5)
    assert tiler.br(1, 1, 1) == (1., 0.5)


def test_bbox(tiler):
    """Bounding boxes of tiles."""
    assert tiler.bbox(0, 0, 0) == (0., 0., 1., 1.)

    assert tiler.bbox(0, 0, 1) == (0., 0., 0.5, 0.5)
    assert tiler.bbox(1, 0, 1) == (0.5, 0., 1., 0.5)
    assert tiler.bbox(0, 1, 1) == (0., 0.5, 0.5, 1.)
    assert tiler.bbox(1, 1, 1) == (0.5, 0.5, 1., 1.)
    
    
def test_quadkey(tiler):
    """Tile to quadkey."""
    assert not tiler.quadkey(0, 0, 0)

    assert tiler.quadkey(0, 0, 1) == '0'
    assert tiler.quadkey(1, 0, 1) == '1'
    assert tiler.quadkey(0, 1, 1) == '2'
    assert tiler.quadkey(1, 1, 1) == '3'


def test_quadkey_to_tile1(tiler):
    """Quadkey to tile exceptions."""
    with pytest.raises(ValueError):
        tiler.quadkey_to_tile('4')

    
def test_quadkey_to_tile2(tiler):
    """Quadkey to tile."""
    assert tiler.quadkey_to_tile('0') == (0, 0, 1)
    assert tiler.quadkey_to_tile('130232101') == (405, 184, 9)
