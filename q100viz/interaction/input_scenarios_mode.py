import pygame

import q100viz.keystone as keystone
import q100viz.session as session
import q100viz.stats as stats
from q100viz.settings.config import config
from q100viz.graphics.graphictools import Image

class Input_Scenarios:
    def __init__(self):
        self.name = 'input_scenarios'
        self.surface = keystone.Surface(session.canvas_size, pygame.SRCALPHA)
        self.surface.src_points = [[0,0], [0,1], [1, 1], [1, 0]]
        self.surface.dst_points = [[0, 0], [0, 100], [100, 100], [100, 0]]

        self.surface.calculate(session.viewport.transform_mat)
        self.images_active = [
            Image("images/scenario_A_active.tif"),
            Image("images/scenario_B_active.tif"),
            Image("images/scenario_C_active.tif"),
            Image("images/scenario_D_active.tif")
            ]
        self.images_disabled = [
            Image("images/scenario_A_disabled.tif"),
            Image("images/scenario_B_disabled.tif"),
            Image("images/scenario_C_disabled.tif"),
            Image("images/scenario_D_disabled.tif")
            ]

        self.images = [image for image in self.images_disabled]

        for lst in [self.images_active, self.images_disabled]:
            for image in lst:
                image.warp()

    def activate(self):
        session.show_polygons = False
        session.show_basemap = False
        session.active_handler = self
        session.environment['mode'] = self.name

        # sliders:
        session.grid_1.slider.show_text = False
        session.grid_1.slider.show_controls = False
        session.grid_2.slider.show_text = True
        session.grid_2.slider.show_controls = True

        # setup mode selectors:
        session.grid_1.update_cell_data(session.input_scenarios_grid_1)
        session.grid_2.update_cell_data(session.input_scenarios_grid_2)

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
        self.images = [image for image in self.images_disabled]

        for grid in [session.grid_1, session.grid_2]:
            for y, row in enumerate(grid.grid):
                for x, cell in enumerate(row):
                    if cell.selected:
                        if y < len(grid.grid) - 1:
                            # assumption: there is only one token to choose the scenario with
                            if grid is session.grid_1 and x < len(row) / 2:
                                self.images[0] = self.images_active[0]
                                session.environment['active_scenario'] = 'A'
                            elif grid is session.grid_1 and x > len(row) / 2:
                                self.images[1] = self.images_active[1]
                                session.environment['active_scenario'] = 'B'
                            elif grid is session.grid_2 and x < len(row) / 2:
                                self.images[2] = self.images_active[2]
                                session.environment['active_scenario'] = 'C'
                            elif grid is session.grid_2 and x > len(row) / 2:
                                self.images[3] = self.images_active[3]
                                session.environment['active_scenario'] = 'D'

                        # set slider handles via selected cell in last row:
                        elif cell.handle is not None:
                            if cell.handle == 'start_input_households':
                                if session.environment['active_scenario'] is not None:
                                    session.handlers['input_households'].activate()
                                else:
                                    print("cannot enter next mode before picking scenario!")

        session.stats.send_simplified_dataframe_with_environment_variables(session.buildings[session.buildings.selected], session.environment)

        print(session.environment)

    def draw(self, canvas):

        if len(session.buildings[session.buildings.selected]):
            # highlight selected buildings
            session.gis.draw_polygon_layer(
                canvas,
                session.buildings[session.buildings.selected], 2, (255, 0, 127)
            )

        # display scenario images:
        x_displace = 65
        for image in self.images:
            canvas.blit(image.image,
                (x_displace,
                (session.canvas_size[1] * config['GRID_1_Y2'] / 100 - image.img_h) / 2))
            x_displace += session.viewport.dst_points[2][0] / 5

    def update(self):
        pass