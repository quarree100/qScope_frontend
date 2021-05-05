import json
import p5

import keystone


class Grid:
    def __init__(self, size, corners):
        self.x_size, self.y_size = size

        # initialize two-dimensional array of grid cells
        self.grid = [[GridCell() for x in range(self.x_size)] for y in range(self.y_size)]

        # create the corner pin surface for projection
        self.surface = keystone.CornerPinSurface(corners)

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

        with p5.push_style():
            try:
                for y, row in enumerate(self.grid):
                    for x, cell in enumerate(row):
                        p5.stroke(stroke)
                        p5.stroke_weight(stroke_weight)
                        p5.fill(p5.Color(*colors[cell.id]) if cell.id > -1 else p5.Color(0, 0, 0, 0))
                        p5.begin_shape()
                        for _x, _y in [[x, y], [x, y + 1], [x + 1, y + 1], [x + 1, y]]:
                            p5.vertex(
                                _x * width / self.x_size,
                                _y * height / self.y_size
                            )
                        p5.end_shape()
            except TypeError:
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
