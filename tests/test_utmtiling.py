import pytest

from tiletanic.tileschemes import UTM10kmTiling

@pytest.fixture
def tiler():
    return UTM10kmTiling()

def test_bounds(tiler):
    """Bounds should encompass the bounds of the UTM zone."""
    assert tiler.bounds.xmin <= 0.
    assert tiler.bounds.xmax >= 1_000_000.
    assert tiler.bounds.ymin <= -10_000_000.
    assert tiler.bounds.ymax >= 10_000_000.

def test_tile(tiler):
    """Tile generation from UTM coordinates and zoom."""

    # Center of the zone should be at 500_000, 0 at every zoom, so
    # check that's the center tile.
    for z in range(0, 19):        
        assert tiler.tile(500_000, 0, z) == (2**z // 2, 2**z // 2, z)

    z = 11 # The 10km zoom level.
    assert tiler.tile(500_000 - 5_000, 0, z) == (2**z // 2 - 1, 2**z // 2, z)
    assert tiler.tile(500_000 + 10_000, 0, z) == (2**z // 2 + 1, 2**z // 2, z)
    assert tiler.tile(500_000, 5_000, z) == (2**z // 2, 2**z // 2 - 1, z)
    assert tiler.tile(500_000, -10_000, z) == (2**z // 2, 2**z // 2 + 1, z)    

def test_parent(tiler):
    """Parent of a tile."""
    assert tiler.parent(0, 0, 1) == (0, 0, 0)
    assert tiler.parent(1, 0, 1) == (0, 0, 0)

    assert tiler.parent(2, 3, 2) == (1, 1, 1)
    assert tiler.parent(3, 0, 2) == (1, 0, 1)


def test_children1(tiler):
    """Children of a level 0 tile."""
    assert set(tiler.children(0, 0, 0)) == {(0, 0, 1),
                                            (1, 0, 1),
                                            (0, 1, 1),
                                            (1, 1, 1)}

    
def test_children2(tiler):
    """Children of a level > 0 tile."""
    assert set(tiler.children(1, 1, 1)) == {(2, 2, 2),
                                            (2, 3, 2),
                                            (3, 2, 2),
                                            (3, 3, 2)}

    
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
    z = 11
    
    assert tiler.ul(2**z // 2, 2**z // 2 - 1, z) == (500_000, 10_000)    
    assert tiler.ul(2**z // 2, 2**z // 2, z) == (500_000, 0)
    assert tiler.ul(2**z // 2, 2**z // 2 + 1, z) == (500_000, -10_000)

    assert tiler.ul(2**z // 2 - 1, 2**z // 2, z) == (490_000, 0)
    assert tiler.ul(2**z // 2 + 1, 2**z // 2, z) == (510_000, 0)

    
def test_br(tiler):
    """Upper left coordinates of input tile."""
    z = 11
    
    assert tiler.br(2**z // 2 - 1, 2**z // 2 - 1, z) == (500_000, 0)
    assert tiler.br(2**z // 2 - 1, 2**z // 2, z) == (500_000, -10_000)
    assert tiler.br(2**z // 2 - 1, 2**z // 2 + 1, z) == (500_000, -20_000)

    assert tiler.br(2**z // 2, 2**z // 2 - 1, z) == (510_000, 0)
    assert tiler.br(2**z // 2 + 1, 2**z // 2 - 1, z) == (520_000, 0)


def test_bbox(tiler):   
    """Bounding boxes of tiles."""
    z = 11
    
    assert tiler.bbox(2**z // 2, 2**z // 2 - 1, z) == (500000, 0, 510000, 10000)
    assert tiler.bbox(2**z // 2, 2**z // 2, z) == (500000, -10000, 510000, 0)
    assert tiler.bbox(2**z // 2 + 1, 2**z // 2 - 1, z) == (510000, 0, 520000, 10000)
    assert tiler.bbox(2**z // 2 - 1, 2**z // 2 + 1, z) == (490000, -20000, 500000, -10000)

    z = 10
    assert tiler.bbox(2**z // 2, 2**z // 2 - 1, z) == (500000, 0, 520000, 20000)

    z = 8
    assert tiler.bbox(2**z // 2, 2**z // 2 - 1, z) == (500000, 0, 580000, 80000)

def test_quadkey_to_tile1(tiler):
    """Quadkey to tile exceptions."""
    with pytest.raises(ValueError):
        tiler.quadkey_to_tile('4')

    
def test_quadkey_to_tile2(tiler):
    """Quadkey to tile."""
    assert tiler.quadkey_to_tile('0') == (0, 0, 1)
    assert tiler.quadkey_to_tile('130232101') == (405, 184, 9)
