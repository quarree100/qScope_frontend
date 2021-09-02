# setup notes
collection of notes used for different experimental setups

## coordinates:

**ROI for distorted polygons:**

``` python
# Initialize geographic viewport and basemap

_gis = session.gis = gis.GIS(canvas_size,
               # northeast          northwest           southwest           southeast
               [[1013622, 7207331], [1013083, 7207150], [1013414, 7206159], [1013990, 7206366]],
               session.viewport)


_gis = session.gis = gis.GIS(canvas_size,
               # northeast          northwest           southwest           southeast
               [[1013640, 7207470], [1013000, 7207270], [1013400, 7206120], [1014040, 7206320]],
               viewport)
```
???

**kleinerer Kartenausschnitt:**

``` python
_gis = session.gis = gis.GIS(canvas_size,
               # northeast          northwest           southwest           southeast
               [[1013578, 7207412], [1013010, 7207210], [1013386, 7206155], [1013953, 7206357]],
               viewport)
```

**mit Input Area am linken Rand und Aussparung unten:**

``` python
_gis = session.gis = gis.GIS(
    canvas_size,
    # northeast          northwest           southwest           southeast
    [[1013554, 7207623], [1012884, 7207413], [1013281, 7206147], [1013952, 7206357]],
    viewport)
```

**mit Input Area am rechten Rand und Aussparung unten:**

``` python
_gis = session.gis = gis.GIS(
    canvas_size,
    # northeast          northwest           southwest           southeast
    [[1013631, 7207409], [1012961, 7207198], [1013359, 7205932], [1014029, 7206143]],
    viewport)
```

## grid

**single grid, upper left:**

``` python
grid_1 = session.grid_1 = grid.Grid(canvas_size, 11, 11, [[50, 50], [50, 0], [75, 0], [75, 50]], viewport)
grid_2 = session.grid_2 = grid.Grid(canvas_size, 22, 22, [[0, 0], [0, 100], [50, 100], [50, 0]], viewport)
```

**16 x 22 grid rechts:**

``` python
grid_1 = session.grid_1 = grid.Grid(canvas_size, 16, 22, [[50, 0], [50, 72], [100, 72], [100, 0]], viewport)
grid_2 = session.grid_2 = grid.Grid(canvas_size, 22, 22, [[0, 0], [0, 100], [50, 100], [50, 0]], viewport)

```

**18 x 22 grid rechts:**

``` python
ncols = 22
nrows = 18
grid_1 = session.grid_1 = grid.Grid(canvas_size, ncols, nrows, [[50, 0], [50, 81], [100, 81], [100, 0]], viewport)
grid_2 = session.grid_2 = grid.Grid(canvas_size, 22, 22, [[0, 0], [0, 100], [50, 100], [50, 0]], viewport)
```