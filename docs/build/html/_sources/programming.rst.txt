Programming
===========
How to program the Q-Scope

File Structure
^^^^^^^^^^^^^^
``session.py`` contains global variables

Setup
^^^^^

coordinates:
------------

**ROI for distorted polygons:**

.. code-block:: python

  # Initialize geographic viewport and basemap

  _gis = session.gis = gis.GIS(canvas_size,
                 # northeast          northwest           southwest           southeast
                 [[1013622, 7207331], [1013083, 7207150], [1013414, 7206159], [1013990, 7206366]],
                 session.viewport)


  _gis = session.gis = gis.GIS(canvas_size,
                 # northeast          northwest           southwest           southeast
                 [[1013640, 7207470], [1013000, 7207270], [1013400, 7206120], [1014040, 7206320]],
                 viewport)

???

**kleinerer Kartenausschnitt:**

.. code-block:: python

  _gis = session.gis = gis.GIS(canvas_size,
                 # northeast          northwest           southwest           southeast
                 [[1013578, 7207412], [1013010, 7207210], [1013386, 7206155], [1013953, 7206357]],
                 viewport)

**mit Input Area am linken Rand und Aussparung unten:**

.. code-block:: python

  _gis = session.gis = gis.GIS(
      canvas_size,
      # northeast          northwest           southwest           southeast
      [[1013554, 7207623], [1012884, 7207413], [1013281, 7206147], [1013952, 7206357]],
      viewport)

**mit Input Area am rechten Rand und Aussparung unten:**

.. code-block:: python

  gis = session.gis = gis.GIS(
      canvas_size,
      # northeast          northwest           southwest           southeast
      [[1013631, 7207409], [1012961, 7207198], [1013359, 7205932], [1014029, 7206143]],
      viewport)

grid
----

**single grid, upper left:**

.. code-block:: python

  grid_1 = session.grid_1 = grid.Grid(canvas_size, 11, 11, [[50, 50], [50, 0], [75, 0], [75, 50]], viewport)
  grid_2 = session.grid_2 = grid.Grid(canvas_size, 22, 22, [[0, 0], [0, 100], [50, 100], [50, 0]], viewport)

**16 x 22 grid rechts:**

.. code-block:: python

  grid_1 = session.grid_1 = grid.Grid(canvas_size, 16, 22, [[50, 0], [50, 72], [100, 72], [100, 0]], viewport)
  grid_2 = session.grid_2 = grid.Grid(canvas_size, 22, 22, [[0, 0], [0, 100], [50, 100], [50, 0]], viewport)

**18 x 22 grid rechts:**

.. code-block:: python

  ncols = 22
  nrows = 18
  grid_1 = session.grid_1 = grid.Grid(canvas_size, ncols, nrows, [[50, 0], [50, 81], [100, 81], [100, 0]], viewport)
  grid_2 = session.grid_2 = grid.Grid(canvas_size, 22, 22, [[0, 0], [0, 100], [50, 100], [50, 0]], viewport)

Drawing on Canvas
^^^^^^^^^^^^^^^^^

**displaying text**:

.. code-block:: python

  # 1. define font:
  font = pygame.font.SysFont('Arial', 20)
  # 2. use font to write to canvas:
  canvas.blit(font.render(str(mouse_pos), True, (255,255,255)), (200,700))

**drawing polygons onto a specific surface**:


.. code-block:: python

  # [[bottom-left], [top-left], [bottom-right], [top-right]]
  #             [[x1, y1], [x1, y2], [x2, y1], [x2, y2]]
  rect_points = [[20, 70], [20, 20], [80, 20], [80, 70]]  # percentage relative to viewport

  #                   surface,   color,      coords_transformed
  pygame.draw.polygon(viewport, (255, 0, 0), viewport.transform(rect_points))

keystone transformation
^^^^^^^^^^^^^^^^^^^^^^^

`tutorial_py_geometric_transformations <https://docs.opencv.org/3.4/da/d6e/tutorial_py_geometric_transformations.html>`_

`using cv.perspectiveTransform for vectors <https://docs.opencv.org/3.4/d2/de8/group__core__array.html#gad327659ac03e5fd6894b90025e6900a7>`_
and `cv.warpPerspective for images <https://docs.opencv.org/3.4/da/d54/group__imgproc__transform.html#gaf73673a7e8e18ec6963e3774e6a94b87>`_

in file ``q100viz/keystone.py``

Sliders
^^^^^^^

recognition/data
----------------

* from cspy via UDP (json)
* definition via ``cityscopy.json``

frontend representation
-----------------------

* slider uses the transformation of the grid
* **drawing of polygons and values** should be done via ``self.surface.blit(...)``. Slider surface is rendered and "blitted" to main canvas.

``print(slider.coords_transformed)`` returns:

.. code-block::

  [[860.9641723632812, 915.1583862304688],
  [863.9833984375, 614.8511352539062],
  [1228.917724609375, 622.6510009765625],
  [1226.5196533203125, 923.7374267578125]]

with ``[[???[x], ???[y]], [upper-left[x], upper-left[y]], [upper-right[x], upper-right[y]], [???[x], ???[y]]]``


Modes
^^^^^
* there are different machine states, defined by the files in ``q100viz/interaction/`` → these are the modes the program is running at (per time)
* states are defined via `session.handlers`
* implemented modes are:
    * CalibrationMode
    * EditMode: deprecated!
    * InputMode
    * SimulationMode

CalibrationMode
---------------

EditMode
--------
...deprecated!

InputMode
---------
general mode for interaction with Tangible User Interface.

examples:
~~~~~~~~~

**increase/decrease value by relative rotation:**

e.g. emission, in ``InputMode.draw()``:

.. code-block:: python

  if cell.id > 0:
     if cell.rel_rot == 1:
         i = get_intersection(session.buildings, grid, x, y)
         session.buildings.loc[i, 'CO2'] += 20
     elif cell.rel_rot == -1:
         i = get_intersection(session.buildings, grid, x, y)
         session.buildings.loc[i, 'CO2'] -= 20

SimulationMode
--------------
... will start the GAMA headless simulation and wait for the results.


API
^^^
JSON and CSV constructs used for the communication between GAMA, the Q-Scope-infoscreen and -frontend.
