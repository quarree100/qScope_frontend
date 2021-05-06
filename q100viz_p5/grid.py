import json
import p5

import keystone


class Grid:
    def __init__(self, xmin, ymin, xmax, ymax, x_size, y_size):
        self.x_size = x_size
        self.y_size = y_size

        # calculate the projection matrix (grid coordinates -> viewport coordinates)
        self.surface = keystone.CornerPinSurface(
            [[0, 0],       [0, y_size],  [x_size, 0],  [x_size, y_size]],
            [[xmin, ymin], [xmin, ymax], [xmax, ymin], [xmax, ymax]    ]
        )

        # initialize two-dimensional array of grid cells
        self.grid = [[GridCell() for x in range(x_size)] for y in range(y_size)]

    def draw(self, stroke, stroke_weight):
        colors = [
            (180, 180, 180),
            (255, 255, 255),
            (50, 50, 125),
            (255, 255, 0),
            (0, 255, 255),
            (0, 100, 255),
            (100, 255, 100)
        ]

        with p5.push_matrix():
            p5.apply_matrix(self.surface.get_transform_mat())

            with p5.push_style():
                try:
                    for y, row in enumerate(self.grid):
                        for x, cell in enumerate(row):
                            p5.stroke(stroke)
                            p5.stroke_weight(stroke_weight * (4 if cell.selected else 1))
                            p5.fill(p5.Color(*colors[cell.id]) if cell.id > -1 else p5.Color(0, 0, 0, 0))
                            p5.rect(x, y, 1, 1)
                except TypeError:
                    pass

    def mouse_pressed(self, v_point):
        # get grid coordinate
        coord = self.surface.inverse_transform([v_point])[0]

        # update cell at cursor position
        try:
            cell = self.grid[int(coord[1])][int(coord[0])]
            cell.selected = not cell.selected
        except IndexError:
            pass

    def read_message(self, message):
        try:
            array = json.loads(message)
        except json.decoder.JSONDecodeError:
            print("Invalid JSON")
            return

        # update grid cells
        try:
            for y, row in enumerate(self.grid):
                for x, cell in enumerate(row):
                    cell.id, cell.rot = array[y * self.y_size + x]
        except TypeError:
            pass
        except IndexError:
            print("Warning: incoming grid has unexpected size")

        # self.print()

    def print(self):
        try:
            for row in self.grid:
                for cell in row:
                    print(f"{cell.id}/{cell.rot}", end="\t")
                print()
            print()
        except TypeError:
            pass


class GridCell:
    def __init__(self, id=-1, rot=-1):
        self.id = id
        self.rot = rot
        self.selected = False
