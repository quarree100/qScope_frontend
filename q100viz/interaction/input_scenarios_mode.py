import pygame
import pandas

import q100viz.keystone as keystone
import q100viz.session as session
import q100viz.api as api
from q100viz.settings.config import config
from q100viz.graphics.graphictools import Image


class Input_Scenarios:
    def __init__(self):
        self.name = 'input_scenarios'
        self.surface = keystone.Surface(session.canvas_size, pygame.SRCALPHA)
        self.surface.src_points = [[0, 0], [0, 1], [1, 1], [1, 0]]
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
        # graphics:
        session.show_polygons = False
        session.show_basemap = False
        session.active_handler = self
        session.environment['mode'] = self.name

        # sliders:
        session.grid_1.sliders['slider1'].show_text = False
        session.grid_1.sliders['slider1'].show_controls = False
        session.grid_2.sliders['slider2'].show_text = True
        session.grid_2.sliders['slider2'].show_controls = True

        # setup mode selectors:
        session.grid_1.update_cell_data(session.input_scenarios_grid_1)
        session.grid_2.update_cell_data(session.input_scenarios_grid_2)

        # send data:
        session.api.send_df_with_session_env(None)

    def process_event(self, event):
        if event.type == pygame.locals.MOUSEBUTTONDOWN:
            session.grid_1.mouse_pressed(event.button)
            session.grid_2.mouse_pressed(event.button)

            session.flag_export_canvas = True
            self.process_grid_change()

    def process_grid_change(self):
        session.buildings_df['selected'] = False
        session.environment['active_scenario_handle'] = 'Ref'
        session.grid_2.grid[18][19].handle = None
        self.images = [image for image in self.images_disabled]

        for grid in [session.grid_1, session.grid_2]:
            for y, row in enumerate(grid.grid):
                for x, cell in enumerate(row):
                    if cell.selected:
                        if y < len(grid.grid) - 1:
                            # assumption: there is only one token to choose the scenario with
                            if grid is session.grid_1 and x < len(row) / 2:
                                self.images[0] = self.images_active[0]
                                session.environment['active_scenario_handle'] = 'A'
                            elif grid is session.grid_1 and x > len(row) / 2:
                                self.images[1] = self.images_active[1]
                                session.environment['active_scenario_handle'] = 'B'
                            elif grid is session.grid_2 and x < len(row) / 2:
                                self.images[2] = self.images_active[2]
                                session.environment['active_scenario_handle'] = 'C'
                            elif grid is session.grid_2 and x > len(row) / 2:
                                self.images[3] = self.images_active[3]
                                session.environment['active_scenario_handle'] = 'D'

                            # create mode selector when a scenario is selected
                            if session.environment['active_scenario_handle'] is not None:
                                session.grid_2.grid[18][19].handle = 'start_buildings_interaction'
                                session.grid_2.grid[18][19].color = pygame.color.Color(
                                    'purple')

                        # set slider handles via selected cell in last row:
                        elif cell.handle is not None:
                            if cell.handle == 'start_buildings_interaction':
                                session.handlers['buildings_interaction'].activate()

        session.api.send_session_env()

        ############## send scenario parameters to infoscreen #########
        # data_wrapper = ['' for i in range(session.num_of_rounds)]
        # for i in range(session.num_of_rounds):
        if session.environment['active_scenario_handle'] is not None:

            scenario_data = {
                'active_scenario_handle': session.environment['active_scenario_handle'],

                'carbon_price_scenario':
                [session.scenario_data[session.environment['active_scenario_handle']].loc['carbon_price_scenario', 'name_human_readable'],
                    session.scenario_data[session.environment['active_scenario_handle']].loc['carbon_price_scenario', 'value_human_readable']],

                'energy_prices_scenario':
                    [session.scenario_data[session.environment['active_scenario_handle']].loc['energy_price_scenario', 'name_human_readable'],
                        session.scenario_data[session.environment['active_scenario_handle']].loc['energy_price_scenario', 'value_human_readable']],

                'q100_price_opex_scenario':
                    [session.scenario_data[session.environment['active_scenario_handle']].loc['q100_price_opex_scenario', 'name_human_readable'],
                        session.scenario_data[session.environment['active_scenario_handle']].loc['q100_price_opex_scenario', 'value_human_readable']],

                'q100_price_capex_scenario':
                    [session.scenario_data[session.environment['active_scenario_handle']].loc['q100_price_capex_scenario', 'name_human_readable'],
                        session.scenario_data[session.environment['active_scenario_handle']].loc['q100_price_capex_scenario', 'value_human_readable']],

                'q100_emissions_scenario':
                    [session.scenario_data[session.environment['active_scenario_handle']].loc['q100_emissions_scenario', 'name_human_readable'],
                        session.scenario_data[session.environment['active_scenario_handle']].loc['q100_emissions_scenario', 'value_human_readable']]
            }

            # data_wrapper[i] = scenario_data
            data_wrapper = {
                'scenario_data': [scenario_data]
            }

            df = pandas.DataFrame(data=data_wrapper)
            session.api.send_dataframe_as_json(df)

    def draw(self, canvas):

        if len(session.buildings_df[session.buildings_df.selected]):
            # highlight selected buildings
            session.gis.draw_polygon_layer(
                canvas,
                session.buildings_df[session.buildings_df.selected], 2, (255, 0, 127)
            )

        # display scenario images:
        x_displace = 65
        for image in self.images:
            canvas.blit(image.image,
                        (x_displace,
                         (session.canvas_size[1] * config['GRID_1_Y2'] / 100 - image.img_h) / 2))
            x_displace += session.viewport.dst_points[2][0] / 5


        x_displace = 260
        font = pygame.font.SysFont('Arial', 20)
        for identifier, title in session.scenario_titles.items():
            canvas.blit(font.render(title, True, (255, 255, 255)),
                        (x_displace, (session.canvas_size[1] * config['GRID_1_Y2'] / 100 - image.img_h) / 2))
            x_displace += session.viewport.dst_points[2][0] / 5


    def update(self):
        pass
