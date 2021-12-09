from pygame.locals import MOUSEBUTTONDOWN

import q100viz.session as session


class TuiMode:
    def __init__(self):
        self.slider_handles = ['year', 'year', 'year',
                        'support', 'support', 'support',
                        'CO2-Preis', 'CO2-Preis', 'CO2-Preis', ' CO2-Preis',
                        'CO2-emissions', 'CO2-emissions', 'CO2-emissions',
                        'technologie', 'technologie', 'technologie',
                        'investment', 'investment', 'investment',
                        'anschluss', 'anschluss', 'anschluss']

        self.slider_handle = self.slider_handles[0]

    def process_event(self, event, config):
        if event.type == MOUSEBUTTONDOWN:
            session.grid_1.mouse_pressed(event.button)
            session.grid_2.mouse_pressed(event.button)

    def draw(self, canvas):
        session.buildings['selected'] = False

        # process grid changes
        for grid in [session.grid_1, session.grid_2]:
            for y, row in enumerate(grid.grid):
                for x, cell in enumerate(row):
                    if cell.selected:
                        # high performance impact, use sparingly
                        i = get_intersection(session.buildings, grid, x, y)

                        # use rotation value to cycle through buildings located in cell
                        n = len(session.buildings[i])
                        if n > 0:
                            selection = session.buildings[i].iloc[cell.rot % n]
                            session.buildings.loc[selection.name, 'selected'] = True

                        # consider last row as slider control
                        if y == len(grid.grid)-1:
                            self.slider_handle = self.slider_handles[x]
                            print("slider_handle: ", self.slider_handle)

                    if cell.id > 0 and cell.rel_rot == 1:
                        i = get_intersection(session.buildings, grid, x, y)
                        session.buildings.loc[i, 'CO2'] += 20  # arbitrarily increase a value associated with that building. TODO: give this some meaning.

        if len(session.buildings[session.buildings.selected]):
            # highlight selected buildings
            session.gis.draw_polygon_layer(
                canvas,
                session.buildings[session.buildings.selected], 2, (255, 0, 127)
            )

    def update_slider(self):
        if session.grid_1.sliders['slider0'] is not None:
            if self.slider_handle == 'year':
                session.environment['year'] = 2020 + int(session.grid_1.sliders['slider0'] * 30)  # ranges from 2020 to 2050
            elif self.slider_handle == 'CO2':
                print("changing %s with slider0" % self.slider_handle)
                # session.environment['year'] = 2020 + int(session.grid_1.sliders['slider0'] * 30)  # ranges from 2020 to 2050
            elif self.slider_handle == 'fun':
                print("changing %s with slider0" % self.slider_handle)
                # session.environment['year'] = 2020 + int(session.grid_1.sliders['slider0'] * 30)  # ranges from 2020 to 2050


def get_intersection(df, grid, x, y):
    # get viewport coordinates of the cell rectangle
    cell_vertices = grid.surface.transform(
        [[_x, _y] for _x, _y in [[x, y], [x + 1, y], [x + 1, y + 1], [x, y + 1]]]
    )
    # find elements intersecting with selected cell
    return session.gis.get_intersection_indexer(df, cell_vertices)