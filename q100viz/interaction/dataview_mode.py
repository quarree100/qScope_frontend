''' The Questionnaire Mode provides questions that are to be answered by the user in order to assess their mindset/positioning towards Renewable Energies and to evaluate their general acceptance of the project. '''

import pygame
import pandas as pd
import json
import numpy

import q100viz.keystone as keystone
import q100viz.session as session
from q100viz.settings.config import config
from q100viz.graphics.graphictools import Image

class DataView_Mode():
    def __init__(self):
        self.name = 'data_view'

        self.images_active = [
            Image("images/piechart.tif"),
            Image("images/predator-prey.tif"),
            Image("images/sankey.tif")
            ]
        self.images_disabled = [
            Image("images/piechart_disabled.tif"),
            Image("images/predator-prey_disabled.tif"),
            Image("images/sankey_disabled.tif")
            ]
        self.images = [image for image in self.images_disabled]

        for lst in [self.images_active, self.images_disabled]:
            for image in lst:
                image.warp()

    def activate(self):
        session.active_handler = self
        session.environment['mode'] = self.name

        session.show_polygons = False
        session.show_basemap = False

        # setup sliders:
        session.grid_1.slider.show_text = False
        session.grid_1.slider.show_controls = False
        session.grid_2.slider.show_text = True
        session.grid_2.slider.show_controls = True

        # setup mode selectors:
        session.grid_1.update_cell_data(session.data_view_grid_1)
        session.grid_2.update_cell_data(session.data_view_grid_2)

        session.stats.send_dataframe_with_environment_variables(None, session.environment)

    def process_event(self, event):
        if event.type == pygame.locals.MOUSEBUTTONDOWN:
            session.grid_1.mouse_pressed(event.button)
            session.grid_2.mouse_pressed(event.button)
            session.stats.send_simplified_dataframe_with_environment_variables(
                session.buildings[session.buildings.selected],
                session.environment)

            self.process_grid_change()

            connected_buildings = pd.DataFrame(data=[
                {'connected_buildings' : len(session.buildings[session.buildings['connection_to_heat_grid'] == True])}])
            session.stats.send_dataframe_as_json(connected_buildings)

    def process_grid_change(self):
        session.buildings['selected'] = False
        for grid in [session.grid_1, session.grid_2]:
            for cell in grid.grid[:][len(grid.grid) - 1]:
                if cell.selected and cell.handle == 'start_input_scenarios':
                    session.handlers['input_scenarios'].activate()

    def draw(self, canvas):
        # display graphs:
        x_displace = 65
        for image in self.images:
            canvas.blit(image.image,
                (x_displace,
                (session.canvas_size[1] * config['GRID_1_Y2'] / 100 - image.img_h) / 3))
            x_displace += session.viewport.dst_points[2][0] / 4
        pass

    def update(self):
        pass