''' The Questionnaire Mode provides questions that are to be answered by the user in order to assess their mindset/positioning towards Renewable Energies and to evaluate their general acceptance of the project. '''

import pygame
import pandas as pd

import q100viz.session as session
from q100viz.graphics.graphictools import Image

class DataViewTotal_Mode():
    def __init__(self):
        self.name = 'total_data_view'

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
        '''do not call! This function is automatically called in main loop. Instead, enable a mode by setting session.active_mode = session.[mode]'''

        session.active_mode = self
        session.environment['mode'] = self.name

        session.show_polygons = True
        session.show_basemap = True

        # setup sliders:
        session.grid_1.sliders['slider0'].show_text = False
        session.grid_1.sliders['slider0'].show_controls = False
        session.grid_1.sliders['slider1'].show_text = False
        session.grid_1.sliders['slider1'].show_controls = False
        session.grid_2.sliders['slider2'].show_text = False
        session.grid_2.sliders['slider2'].show_controls = True
        session.grid_2.sliders['slider3'].show_text = False
        session.grid_2.sliders['slider3'].show_controls = True

        # setup mode selectors:
        session.grid_1.update_cell_data(session.total_data_view_grid_1)
        session.grid_2.update_cell_data(session.total_data_view_grid_2)

        session.api.send_session_env()

    def process_event(self, event):
        if event.type == pygame.locals.MOUSEBUTTONDOWN:
            session.grid_1.mouse_pressed(event.button)
            session.grid_2.mouse_pressed(event.button)
            session.api.send_simplified_dataframe_with_environment_variables(
                session.buildings.df[session.buildings.df.selected],
                session.environment)

            self.process_grid_change()

            connected_buildings = pd.DataFrame(data=[
                {'connected_buildings' : len(session.buildings.df[session.buildings.df['connection_to_heat_grid'] != False])}])
            session.api.send_dataframe_as_json(connected_buildings)

    def process_grid_change(self):
        session.buildings.df['selected'] = False
        for grid in [session.grid_1, session.grid_2]:
            for y, row in enumerate(grid.grid):
                for x, cell in enumerate(row):
                    if cell.selected:
                        if cell.handle == 'start_individual_data_view':
                            session.active_mode = session.individual_data_view
                        elif cell.handle == 'start_buildings_interaction':
                            session.active_mode = session.buildings_interaction


    def draw(self, canvas):

        try:
            # highlight selected buildings (draws colored stroke on top)
            if len(session.buildings.df[session.buildings.df.selected]):

                sel_buildings = session.buildings.df[(session.buildings.df.selected)]
                for building in sel_buildings.to_dict('records'):
                    fill_color = pygame.Color(session.user_colors[int(building['group'])])

                    points = session._gis.surface.transform(building['geometry'].exterior.coords)
                    pygame.draw.polygon(session._gis.surface, fill_color, points, 2)

        except Exception as e:
                print("Cannot draw frontend:", e)
                session.log += "\nCannot draw frontend: %s" % e

        font = pygame.font.SysFont('Arial', 18)
        nrows = 22

        column = 16
        row = 14
        font = pygame.font.SysFont('Arial', 18)
        canvas.blit(font.render(
            "Individualdaten", True, pygame.Color(255,255,255)),
            (session.grid_2.rects_transformed[column+nrows*row][1][0][0] + 5,
             session.grid_2.rects_transformed[column+nrows*row][1][0][1] + 10)
        )

        column = 17
        row = 18
        font = pygame.font.SysFont('Arial', 18)
        canvas.blit(font.render(
            "Interaktion", True, pygame.Color(255,255,255)),
            (session.grid_2.rects_transformed[column+nrows*row][1][0][0] + 8,
             session.grid_2.rects_transformed[column+nrows*row][1][0][1] + 10)
        )

    def update(self):
        pass