# qScope_frontend manual
very messy, though.

## files

- `session.py` contains global variables

## handlers

see "machine states"

## machine states

- there are different machine states, defined by the files in `q100viz/interaction/` → these are the modes the program is running at (per time)
- states are defined via `session.handlers`
- implemented modes are:
    - CalibrationMode
    - EditMode: deprecated!
    - InputMode
    - SimulationMode

### CalibrationMode

### EditMode
...deprecated!

### InputMode

general mode for interaction with Tangible User Interface.

#### examples:

**increase/decrease value by relative rotation:**

e.g. emission, in `InputMode.draw()`:

``` python
 if cell.id > 0:
     if cell.rel_rot == 1:
         i = get_intersection(session.buildings, grid, x, y)
         session.buildings.loc[i, 'CO2'] += 20
     elif cell.rel_rot == -1:
         i = get_intersection(session.buildings, grid, x, y)
         session.buildings.loc[i, 'CO2'] -= 20
```

### SimulationMode


## drawing on canvas

**displaying text**:
``` python
# 1. define font:
font = pygame.font.SysFont('Arial', 20)
# 2. use font to write to canvas:
canvas.blit(font.render(str(mouse_pos), True, (255,255,255)), (200,700))
```

**drawing polygons onto a specific surface**:
``` python
# [[bottom-left], [top-left], [bottom-right], [top-right]]
#             [[x1, y1], [x1, y2], [x2, y1], [x2, y2]]
rect_points = [[20, 70], [20, 20], [80, 20], [80, 70]]  # percentage relative to viewport

#                   surface,   color,      coords_transformed
pygame.draw.polygon(viewport, (255, 0, 0), viewport.transform(rect_points))
```

## keystone transformation
https://docs.opencv.org/3.4/da/d6e/tutorial_py_geometric_transformations.html

using [cv.perspectiveTransform](https://docs.opencv.org/3.4/d2/de8/group__core__array.html#gad327659ac03e5fd6894b90025e6900a7) for vectors and
[cv.warpPerspective](https://docs.opencv.org/3.4/da/d54/group__imgproc__transform.html#gaf73673a7e8e18ec6963e3774e6a94b87) for images

in file `q100viz/keystone.py`


## sliders

### recognition/data

- from cspy via UDP (json)
- definition via cityscopy.json

### frontend representation

- slider uses the transformation of the grid
- **drawing of polygons and values** should be done via `self.surface.blit(...)`. Slider surface is rendered and "blitted" to main canvas.

`print(slider.coords_transformed)` returns:

`[[860.9641723632812, 915.1583862304688], [863.9833984375, 614.8511352539062], [1228.917724609375, 622.6510009765625], [1226.5196533203125, 923.7374267578125]]`,
with [[???[x], ???[y]], [upper-left[x], upper-left[y]], [upper-right[x], upper-right[y]], [???[x], ???[y]]]