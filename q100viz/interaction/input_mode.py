''' The Input Mode displays everything needed for standard User Interaction '''

import pygame

import q100viz.keystone as keystone
import q100viz.session as session
from config import config


class InputMode:
    def __init__(self):

        self.slider_handle = session.slider_handles[0]

    def process_event(self, event, config):
        if event.type == pygame.locals.MOUSEBUTTONDOWN:
            session.grid_1.mouse_pressed(event.button)
            session.grid_2.mouse_pressed(event.button)
            session.print_verbose(session.buildings)
            session.flag_export_canvas = True

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
                            session.buildings.loc[selection.name,
                                                  'selected'] = True

                        # define slider control via selected cell in last row:
                        if y == len(grid.grid)-1:
                            self.slider_handle = session.slider_handles[
                                int(x/len(session.slider_handles))]
                            session.print_verbose(
                                ("slider_handle: ", self.slider_handle))

        if len(session.buildings[session.buildings.selected]):
            # highlight selected buildings
            session.gis.draw_polygon_layer(
                canvas,
                session.buildings[session.buildings.selected], 2, (255, 0, 127)
            )

    def update(self):
        # update slider:
        if session.grid_1.sliders['slider0'] is not None:
            if self.slider_handle == 'year':
                # ranges from 2020 to 2050
                session.environment['year'] = 2020 + \
                    int(session.grid_1.sliders['slider0'] * 30)
            elif self.slider_handle == 'foerderung':
                session.environment['foerderung'] = int(
                    session.grid_1.sliders['slider0'] * 10000)  # ranges from 0 to 10,000€
            elif self.slider_handle == 'CO2-Preis':
                session.environment['CO2-Preis'] = 55 + \
                    session.grid_1.sliders['slider0'] * \
                    195  # ranges from 55 to 240€/t
            elif self.slider_handle == 'CO2-emissions':
                session.buildings.loc[(
                    session.buildings.selected == True), 'CO2'] = session.grid_1.sliders['slider0']  # sets CO2-value of selected buildings to slider value (absolute)
                session.print_verbose((session.buildings[session.buildings['selected'] == True]))
            elif self.slider_handle == 'versorgung':
                if session.grid_1.sliders['slider0'] >= 0 and session.grid_1.sliders['slider0'] < 0.33:
                    session.buildings.loc[(session.buildings.selected == True), 'versorgung'] = 'konventionell'
                elif session.grid_1.sliders['slider0'] >= 0.33 and session.grid_1.sliders['slider0'] < 0.66:
                    session.buildings.loc[(session.buildings.selected == True), 'versorgung'] = 'medium'
                if session.grid_1.sliders['slider0'] >= 0.66 and session.grid_1.sliders['slider0'] < 1:
                    session.buildings.loc[(session.buildings.selected == True), 'versorgung'] = 'gruen'
            elif self.slider_handle == 'investment':
                # ranges from 0 to 10,000€
                session.environment['investment'] = session.grid_1.sliders['slider0'] * 10000
            elif self.slider_handle == 'anschluss':
                session.buildings.loc[(
                    session.buildings.selected == True), 'anschluss'] = session.grid_1.sliders['slider0'] > 0.5  # sets CO2-value of selected buildings to slider value (absolute)
                session.print_verbose((session.buildings[session.buildings['selected'] == True]))

def get_intersection(df, grid, x, y):
    # get viewport coordinates of the cell rectangle
    cell_vertices = grid.surface.transform(
        [[_x, _y] for _x, _y in [[x, y], [x + 1, y], [x + 1, y + 1], [x, y + 1]]]
    )
    # find elements intersecting with selected cell
    return session.gis.get_intersection_indexer(df, cell_vertices)