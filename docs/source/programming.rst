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

  # general:
  # points = [[x1, y1], [x1, y2], [x2, y1], [x2, y2]]
  #          [[bottom-left], [top-left], [bottom-right], [top-right]]
  # points_transformed = reference_surface.transform(points)
  # pygame.draw.polygon(reference_surface, color, points_transformed)

  # example:
  points = [[20, 70], [20, 20], [80, 20], [80, 70]]  # percentage relative to surface
  points_transformend = session.grid_1.surface.transform(points)

  #                   surface,   color,      coords_transformed
  pygame.draw.polygon(viewport, (255, 0, 0), viewport.transform(rect_points))

**display image**
Pygame is able to load images onto Surface objects from PNG, JPG, GIF, and BMP image files.

.. code-block:: python

  image = pygame.image.load("images/scenario_progressive.bmp")
  canvas.blit(image, (0,0))


**display sliders**:
The sliders have a bool called ``show_text`` that, when ``True``, activates the display of the slider control texts. This variable can be used for the usage modes to define whether the slider controls shall be displayed.


keystone transformation
^^^^^^^^^^^^^^^^^^^^^^^

general information on image transofrmation using opencv:

`tutorial_py_geometric_transformations <https://docs.opencv.org/3.4/da/d6e/tutorial_py_geometric_transformations.html>`_

`using cv.perspectiveTransform for vectors <https://docs.opencv.org/3.4/d2/de8/group__core__array.html#gad327659ac03e5fd6894b90025e6900a7>`_
and `cv.warpPerspective for images <https://docs.opencv.org/3.4/da/d54/group__imgproc__transform.html#gaf73673a7e8e18ec6963e3774e6a94b87>`_

adding a new surface, draw on it and transform it:
--------------------------------------------------

.. code-block::

  class SomeClass:
    # session.canvas_size = 1920, 1080
    self.surface = keystone.Surface(session.canvas_size, pygame.SRCALPHA)

    # x_size, y_size = 22, 22
    self.surface.src_points = [[0, 0], [0, y_size], [x_size, y_size], [x_size, 0]]
    self.surface.dst_points = [
        [config['X1'], config['Y1']],
        [config['X1'], config['Y2']],
        [config['X2'], config['Y2']],
        [config['X2'], config['Y1']]]
    # where e.g. X1 = 0, X2 = 50, Y1 = 0, Y2 = 81.818

    def draw(self, viewport):

      pygame.draw.polygon(self.surface, pygame.Color(255, 255, 255), [[20, 70], [20, 20], [80, 20], [80, 70]])  # render polygon

      viewport.blit(self.surface, (0,0))  # cast it to viewport

in file ``q100viz/keystone.py``

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

with ``[[bottom-left[x], bottom-left[y]], [upper-left[x], upper-left[y]], [upper-right[x], upper-right[y]], [bottom-right[x], bottom-right[y]]]``


Modes
^^^^^
* there are different machine states, defined by the files in ``q100viz/interaction/`` → these are the modes the program is running at (per time)
* implemented modes are:
    * CalibrationMode_
    * EditMode_: deprecated!
    * InputMode_
    * SimulationMode_
    * QuestionnaireMode_

each mode has a function called ``activate()`` which is used to (re-)active the mode and set the specific display settings accordingly. Do I want to see a slider (or two)? Shall the basemap be visible? Define it here.
The ``__init__`` function is seldomly used, since it will be run in the beginning of the script (in ``session.py``), before the variables (e.g. ``grid``) are initialized.

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

  if cell.id < 4:
     if cell.rel_rot == 1:
         i = get_intersection(session.buildings, grid, x, y)
         session.buildings.loc[i, 'CO2'] += 20
     elif cell.rel_rot == -1:
         i = get_intersection(session.buildings, grid, x, y)
         session.buildings.loc[i, 'CO2'] -= 20

SimulationMode
--------------
... will start the GAMA headless simulation and wait for the results.
You will have to have [GAMA](https://gama-platform.org/download) installed. It's best to choose the Version with JDK.
Q-Scope needs to know where to find the ``gama-headless.sh`` file, which can be found in the extracted folder ``gama/headless``. Set this up in ``config.py``, providing the headless folder and the location of the gama model file:

.. code-block:: python

  'GAMA_HEADLESS_FOLDER' : '/home/qscope/GAMA/headless/',
  'GAMA_MODEL_FILE' : '../q100_abm/q100/models/qscope_ABM.gaml',

**ATTENTION**: make sure to set the user rights of ``gama-headless.sh`` executable via ``chmod u+x gama-headless.sh``

QuestionnaireMode
-----------------
In this mode, the user will be confronted with questions that can be asked either
- via slider (only one or two user/s at a time)
- via grid (multiple users, using individual tokens)
(the options are yet to be decided)

ModeSelector
^^^^^^^^^^^^

A ModeSelector is a specific cell on the grid, which, when selected via token, activates a certain Mode.

``grid_1_setup.csv``, ``grid_2_setup.csv``, ``input_scenarios_grid_1.csv`` and ``input_scenarios_grid_1.csv`` are used to assign functionality to grid cells.

valid handles are:

**environment handles:**

.. csv-table:: environment handles
  :header: "parameter", "possible values"
  :widths: auto

  "alpha_scenario", "Static_mean, Dynamic_moderate, Dynamic_high, Static_high"
  carbon_price_scenario, "A - Conservative, B - Moderate, C1 - Progressive, C2 - Progressive, C3 - Progressive"
  energy_price_scenario, "Prices_Project start, Prices_2021, Prices_2022 1st half"
  q100_price_opex_scenario, "12 ct / kWh (static), 15-9 ct / kWh (dynamic)"
  q100_price_capex_scenario, "1 payment, 2 payments, 5 payments"
  q100_emissions_scenario, "Constant_50g / kWh, Declining_Steps, Declining_Linear, ``Constant_ Zero emissions``"


**household-individual handles:**

.. csv-table:: household-individual handles
  :header: "adjustable", "parameter", "possible values"
  :widths: auto

  o, my_heat_consumption, float
  o, my_power_consumption, float
  o, my_heat_expenses, float
  o, my_power_expenses, float
  o, my_heat_emissions, float
  o, my_power_emissions, float
  o, my_energy_emissions, float
  ✓, mod_status, "'u', 's'"
  ✓, spec_heat_consumption, float
  ✓, spec_power_consumption, float
  ✓, energy_source,"gas, oil, None"

zusätzlich kann `save_energy` eingestellt werden als Einstellung von Agentenverhalten (TODO!)

**questionnaire**:

- 'answer' (deprecated?)

**mode selection**:

- 'start_input_scenarios' (starts input mode A for global parameters)
- 'start_input_households' (input mode B for individual household parameters)
- 'start_simulation' (creates xml to start GAMA simulation)

**colors** can be set using strings from this list: https://www.pygame.org/docs/ref/color_list.html

The Modes can be switched using either the input keys:
* T: InputMode_ (TUI Mode)
* C: CalibrationMode_
* S: Simulation


API
^^^
JSON and CSV constructs used for the communication between GAMA, the Q-Scope-infoscreen and -frontend.


Starting the GAMA Simulation via XML
------------------------------------
When moving from Input Mode to Simulation Mode (by Placing a Token on the according ModeSelector_), an xml file is composed containing all the global environment data. The general structure looks like this:

.. code-block:: xml

  <Experiment>
    <Parameter name="year">0</Parameter>
    <Parameter name="foerderung">0</Parameter>
    <Parameter name="CO2-Preis">0</Parameter>
    <Parameter name="CO2-emissions">0</Parameter>
    <Parameter name="versorgung">0</Parameter>
    <Parameter name="investment">0</Parameter>
    <Parameter name="anschluss">0</Parameter>
    <Parameter name="connection_speed">0</Parameter>
  </Experiment>


Composing the xml struct is done via ``stats.to_xml`` and receives single rows of a dataframe.

.. code-block:: python

  def to_xml(row):
    xml = ['<Experiment>']
    for field in row.index:
        xml.append('  <Parameter name="{0}">{1}</Parameter>'.format(field, row[field]))
    xml.append('</Experiment>')
    return '\n'.join(xml)

and then in `input_mode.py`:

.. code-block:: python

    # enter simulation mode:
  elif x == int(session.grid_settings['ncols'] * 2 / 3 + 2):
      session.active_mode = session.simulation
      grid.deselect(int(session.grid_settings['ncols'] * 2 / 3), len(grid.grid) - 1)
      print(session.active_mode)

      # compose dataframe to start
      df = pd.DataFrame(session.environment, index=[0])
      xml = '\n'.join(df.apply(stats.to_xml, axis=1))
      print(xml)
      f = open('../data/simulation_df.xml', 'w')
      f.write(xml)
      f.close()
