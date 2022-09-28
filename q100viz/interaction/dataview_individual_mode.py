''' The Questionnaire Mode provides questions that are to be answered by the user in order to assess their mindset/positioning towards Renewable Energies and to evaluate their general acceptance of the project. '''

import pygame
import pandas as pd

import q100viz.session as session
from q100viz.graphics.graphictools import Image

class DataViewIndividual_Mode():
    def __init__(self):
        self.name = 'individual_data_view'

        # self.images_active = [
        #     Image("images/piechart.tif"),
        #     Image("images/predator-prey.tif"),
        #     Image("images/sankey.tif")
        #     ]
        # self.images_disabled = [
        #     Image("images/piechart_disabled.tif"),
        #     Image("images/predator-prey_disabled.tif"),
        #     Image("images/sankey_disabled.tif")
        #     ]
        # self.images = [image for image in self.images_disabled]

        # for lst in [self.images_active, self.images_disabled]:
        #     for image in lst:
        #         image.warp()

    def activate(self):
        session.active_handler = self
        session.environment['mode'] = self.name

        session.show_polygons = False
        session.show_basemap = False

        # setup sliders:
        session.grid_1.sliders['slider0'].show_text = False
        session.grid_1.sliders['slider0'].show_controls = False
        session.grid_1.sliders['slider1'].show_text = False
        session.grid_1.sliders['slider1'].show_controls = False
        session.grid_2.sliders['slider2'].show_text = False
        session.grid_2.sliders['slider2'].show_controls = True

        # setup mode selectors:
        session.grid_1.update_cell_data(session.individual_data_view_grid_1)
        session.grid_2.update_cell_data(session.individual_data_view_grid_2)

        session.api.send_session_env()

        data_view_individual_data = pd.DataFrame(data={
            "data_view_individual_data" : [session.buildings.make_buildings_groups_dict()]})
        session.api.send_dataframe_as_json(data_view_individual_data)

    def process_event(self, event):
        if event.type == pygame.locals.MOUSEBUTTONDOWN:
            session.grid_1.mouse_pressed(event.button)
            session.grid_2.mouse_pressed(event.button)
            session.api.send_simplified_dataframe_with_environment_variables(
                session.buildings.df[session.buildings.df.selected],
                session.environment)

            self.process_grid_change()

            # connected_buildings = pd.DataFrame(data=[
            #     {'connected_buildings' : len(session.buildings[session.buildings['connection_to_heat_grid'] != False])}])
            # session.api.send_dataframe_as_json(connected_buildings)

    def process_grid_change(self):
        session.buildings.df['selected'] = False
        for grid in [session.grid_1, session.grid_2]:
            for y, row in enumerate(grid.grid):
                for x, cell in enumerate(row):
                    if cell.selected:
                        if cell.handle == 'start_total_data_view':
                            session.handlers['total_data_view'].activate()
                        elif cell.handle == 'start_buildings_interaction':
                            session.handlers['buildings_interaction'].activate()

        data_view_individual_data = pd.DataFrame(data={
            "data_view_individual_data" : [session.buildings.make_buildings_groups_dict()]})
        session.api.send_dataframe_as_json(data_view_individual_data)


    def draw(self, canvas):
        # # display graphs:
        # x_displace = 65
        # for image in self.images:
        #     canvas.blit(image.image,
        #         (x_displace,
        #         (session.canvas_size[1] * config['GRID_1_Y2'] / 100 - image.img_h) / 3))
        #     x_displace += session.viewport.dst_points[2][0] / 4

        # display timeline handles:  # TODO: very weird cell accessing... do this systematically!
        font = pygame.font.SysFont('Arial', 18)
        canvas.blit(font.render("Quartiersdaten", True, pygame.Color(255,255,255)), session.grid_2.rects_transformed[20*14][1][0])  # [x*y][1=coords][0=bottom-left]
        # canvas.blit(font.render("Individualdaten", True, pygame.Color(255,255,255)), session.grid_2.rects_transformed[20*14+44][1][0])
        canvas.blit(font.render("Interaktion", True, pygame.Color(255,255,255)), session.grid_2.rects_transformed[20*14+133][1][0])

    def update(self):
        pass