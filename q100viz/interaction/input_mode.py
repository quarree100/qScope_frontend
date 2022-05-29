''' The Input Mode displays everything needed for standard User Interaction '''

import pygame
import pandas as pd
import cv2

import q100viz.keystone as keystone
import q100viz.session as session
import q100viz.stats as stats
from config import config
class Input_Households:
    def __init__(self):
        self.name = 'input_households'

    def activate(self):
        session.show_polygons = True
        session.show_basemap = True
        session.active_handler = session.handlers['input_households']
        session.environment['mode'] = self.name

        # sliders:
        for slider in session.grid_1.slider, session.grid_2.slider:
            slider.show_text = True
            slider.show_controls = True

        # setup mode selectors:
        session.grid_1.update_cell_data(session.input_households_grid_1)
        session.grid_2.update_cell_data(session.input_households_grid_2)

        # send data:
        session.stats.send_dataframe_with_environment_variables(None, session.environment)

    def process_event(self, event):
            if event.type == pygame.locals.MOUSEBUTTONDOWN:
                session.grid_1.mouse_pressed(event.button)
                session.grid_2.mouse_pressed(event.button)

                session.flag_export_canvas = True
                self.process_grid_change()

    def process_grid_change(self):
        session.buildings['selected'] = False
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

                        # set slider handles via selected cell in last row:
                        if cell.handle is not None:
                            if cell.handle in ['connection_to_heat_grid', 'electricity_supplier', 'refurbished', 'environmental_engagement']:
                                if grid.slider.show_controls:
                                    session.grid_2.slider.handle = cell.handle
                                    if grid.slider.previous_handle is not grid.slider.handle:
                                        session.print_verbose(
                                            ("slider_handle: ", grid.slider.handle))
                                        grid.slider.previous_handle = grid.slider.handle

                            elif cell.handle == 'start_input_environment':
                                session.handlers['input_environment'].activate()

                            elif cell.handle == 'start_simulation':
                                session.handlers['simulation'].activate()

        session.stats.send_simplified_dataframe_with_environment_variables(session.buildings[session.buildings.selected], session.environment)

    def draw(self, canvas):

        if len(session.buildings[session.buildings.selected]):
            # highlight selected buildings
            session.gis.draw_polygon_layer(
                canvas,
                session.buildings[session.buildings.selected], 2, (255, 0, 127)
            )

        # coloring slider area:
        for slider in session.grid_1.slider, session.grid_2.slider:
            slider.draw_area()

    def update(self):
        pass

def get_intersection(df, grid, x, y):
    # get viewport coordinates of the cell rectangle
    cell_vertices = grid.surface.transform(
        [[_x, _y] for _x, _y in [[x, y], [x + 1, y], [x + 1, y + 1], [x, y + 1]]]
    )
    # find elements intersecting with selected cell
    return session.gis.get_intersection_indexer(df, cell_vertices)


class Input_Environment:
    def __init__(self):
        self.name = 'input_environment'
        self.surface = keystone.Surface(session.canvas_size, pygame.SRCALPHA)
        self.surface.src_points = [[0,0], [0,1], [1, 1], [1, 0]]
        self.surface.dst_points = [[0, 0], [0, 100], [100, 100], [100, 0]]

        self.surface.calculate(session.viewport.transform_mat)
        self.images = [
            Image("images/scenario_conservative.tif"),
            Image("images/scenario_moderat_I.tif"),
            Image("images/scenario_moderat_II.tif"),
            Image("images/scenario_progressive.tif")
            ]

        for image in self.images:
            image.warp()

    def activate(self):
        session.show_polygons = False
        session.show_basemap = False
        session.active_handler = session.handlers['input_environment']
        session.environment['mode'] = self.name

        # sliders:
        session.grid_1.slider.show_text = False
        session.grid_1.slider.show_controls = False
        session.grid_2.slider.show_text = False
        session.grid_2.slider.show_controls = False

        # setup mode selectors:
        session.grid_1.update_cell_data(session.input_environment_grid_1)
        session.grid_2.update_cell_data(session.input_environment_grid_2)

        # send data:
        session.stats.send_dataframe_with_environment_variables(None, session.environment)

    def process_event(self, event):
            if event.type == pygame.locals.MOUSEBUTTONDOWN:
                session.grid_1.mouse_pressed(event.button)
                session.grid_2.mouse_pressed(event.button)

                session.flag_export_canvas = True
                self.process_grid_change()

    def process_grid_change(self):
        session.buildings['selected'] = False
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

                        # set slider handles via selected cell in last row:
                        if cell.handle is not None:
                            if cell.handle in cell.handle in ['renovation_cost', 'CO2-prize']:  # TODO: provide valid handles somewhere globally..
                                if grid.slider.show_controls:
                                    grid.slider.handle = cell.handle
                                    if grid.slider.previous_handle is not grid.slider.handle:
                                        session.print_verbose(
                                            ("slider_handle: ", grid.slider.handle))
                                        grid.slider.previous_handle = grid.slider.handle

                            elif cell.handle == 'start_input_households':
                                session.handlers['input_households'].activate()

                            elif cell.handle == 'start_simulation':
                                session.handlers['simulation'].activate()

        session.stats.send_simplified_dataframe_with_environment_variables(session.buildings[session.buildings.selected], session.environment)

    def draw(self, canvas):

        if len(session.buildings[session.buildings.selected]):
            # highlight selected buildings
            session.gis.draw_polygon_layer(
                canvas,
                session.buildings[session.buildings.selected], 2, (255, 0, 127)
            )

        # coloring slider area:
        for slider in session.grid_1.slider, session.grid_2.slider:
            slider.draw_area()

        # display images:
        x_displace = 65
        for image in self.images:
            canvas.blit(image.image,
                (x_displace,
                (session.canvas_size[1] * config['GRID_1_Y2'] / 100 - image.img_h) / 2))
            x_displace += session.viewport.dst_points[2][0] / 5

    def update(self):
        pass


class Image:
    def __init__(self, file):
        self.file = file
        self.surface = keystone.Surface(session.canvas_size)

        self.img_h, self.img_w, _ = cv2.imread(file).shape

        # calculate the projection matrix (image pixels -> EPSG:3857)
        self.surface.src_points = [[0, 0], [0, self.img_h], [self.img_w, self.img_h], [self.img_w, 0]]

        x_2 = self.img_w/session.canvas_size[0] * 100
        y_2 = self.img_h/session.canvas_size[1] * 100
        self.surface.dst_points = [[0, 0], [0, y_2], [x_2, y_2], [x_2, 0]]
        self.surface.calculate(session.viewport.transform_mat)

    def warp(self):
        # warp image and update the surface
        image = self.surface.warp_image(self.file, session.canvas_size)
        self.image = pygame.image.frombuffer(image, image.shape[1::-1], 'BGR')
        self.image.set_colorkey((0, 0, 0))