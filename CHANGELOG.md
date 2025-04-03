# 1.1.0 (2020-01-03)
- Added new UTM5kmTiling tilescheme which aligns to the Maxar Analysis
  Ready Data (ARD) grid.

# 1.0.0 (2019-08-14)
- Added new UTM10kmTiling and UTM100kmTiling tile schemes. This
  provides MGRS-like tilings at a particular zoom level in the
  quadtree.
- Added multi zoom level capacity. Now you can pass several zoom
  levels to cover_geometry and it will generate the biggest tiles
  availables using those zoom levels. Example:

        tilecover.cover_geometry(tiler, geom, [16, 17, 19])

- Tiletanic now requires python >= 3.6

# 0.0.5 (2016-04-20)
- Added new tilecover CLI.  To learn more, run

        tiletanic cover-geometry --help

# 0.0.4 (2015-11-07)
- Added new WebMercator tile scheme

# 0.0.3 (2015-11-04)
- Initial Release with DGTiling tile scheme
