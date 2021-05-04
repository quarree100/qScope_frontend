import json
import p5

import keystone


class Grid:
    def __init__(self, size, corners):
        self.x_size, self.y_size = size

        # each grid cell is a tuple representing (ID, rotation)
        self.grid = [[(-1, -1)] * self.y_size] * self.x_size

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
                    for x, (id, rot) in enumerate(row):
                        p5.stroke(stroke)
                        p5.stroke_weight(stroke_weight)
                        p5.fill(p5.Color(*colors[id]) if id > -1 else p5.Color(0, 0, 0, 0))
                        p5.begin_shape()
                        for _x, _y in [(x, y), (x, y + 1), (x + 1, y + 1), (x + 1, y)]:
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

        # convert flat list to two-dimensional grid
        self.grid = [array[i:i + self.x_size] for i in range(0, len(array), self.x_size)]

        # self.print()

    def print(self):
        try:
            for row in self.grid:
                for cell in row:
                    print("/".join(map(str, cell)), end="\t")
                print()
            print()
        except TypeError:
            pass
