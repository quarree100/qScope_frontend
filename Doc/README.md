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
    - CalibrationMode:
    - EditMode: deprecated!
    - InputMode:
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
font = pygame.font.SysFont('Arial', 20)  # 1. define font
canvas.blit(font.render(str(mouse_pos), True, (255,255,255)), (200,700))  # 2. use font to write to canvas
```

**drawing polygons**:

`pygame.draw.polygon(self.surface, self.color, self.coords_transformed)`

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