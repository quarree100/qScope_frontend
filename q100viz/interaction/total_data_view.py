''' The Questionnaire Mode provides questions that are to be answered by the user in order to assess their mindset/positioning towards Renewable Energies and to evaluate their general acceptance of the project. '''

import pygame
import pandas as pd
import datetime

import q100viz.session as session

class DataViewTotal_Mode():
    def __init__(self):
        self.name = 'total_data_view'
        self.mode_token_selection_time = datetime.datetime.now()
        self.activation_buffer_time = 2  # seconds before simulation begins

    def activate(self):
        '''do not call! This function is automatically called in main loop. Instead, enable a mode by setting session.active_mode = session.[mode]'''

        session.environment['mode'] = self.name
        for mode in session.modes:
            mode.waiting_to_start = False

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
            session.api.send_df_with_session_env(
                session.buildings.df[session.buildings.df.selected])

            self.process_grid_change()

            connected_buildings = pd.DataFrame(data=[
                {'connected_buildings' : len(session.buildings.df[session.buildings.df['connection_to_heat_grid'] != False])}])
            session.api.send_dataframe_as_json(connected_buildings)

    def process_grid_change(self):

        session.buildings.df['selected'] = False

        for x,y,cell,grid in session.iterate_grids():
            if cell.selected:

                # mode selectors:
                if cell.handle in session.MODE_SELECTOR_HANDLES:
                    mode = session.string_to_mode(cell.handle[6:])
                    if not mode.waiting_to_start:
                        self.mode_token_selection_time = datetime.datetime.now()
                        mode.waiting_to_start = True

            elif cell.handle in session.MODE_SELECTOR_HANDLES:  # interrupt buffer when deselected
                mode = session.string_to_mode(cell.handle[6:])
                mode.waiting_to_start = False

        session.api.send_session_env()


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
        row = 13
        font = pygame.font.SysFont('Arial', 18)
        canvas.blit(font.render(
            "Individualdaten", True, pygame.Color(255,255,255)),
            (session.grid_2.rects_transformed[column+nrows*row][1][0][0] + 5,
             session.grid_2.rects_transformed[column+nrows*row][1][0][1] + 10)
        )

        column = 17
        row = 17
        font = pygame.font.SysFont('Arial', 18)
        canvas.blit(font.render(
            "Interaktion", True, pygame.Color(255,255,255)),
            (session.grid_2.rects_transformed[column+nrows*row][1][0][0] + 8,
             session.grid_2.rects_transformed[column+nrows*row][1][0][1] + 10)
        )

        # mode buffer:
        column = 20
        for mode, row in zip(session.modes, [18, 16, 14, 12]):
            if mode.waiting_to_start:
                sim_string = str(round(mode.activation_buffer_time -(datetime.datetime.now() - self.mode_token_selection_time).total_seconds(), 2))
                canvas.blit(font.render(sim_string, True, pygame.Color(255,255,255)), session.grid_2.rects_transformed[column+nrows*row][1][0])

    def update(self):
        for mode in session.modes:
            if mode.waiting_to_start:
                if (datetime.datetime.now() - self.mode_token_selection_time).total_seconds() > mode.activation_buffer_time and (datetime.datetime.now() - self.mode_token_selection_time).total_seconds() < 10:
                    for mode_ in session.modes:
                        mode_.waiting_to_start = False

                    if mode is session.simulation:
                        session.simulation.setup()
                    session.active_mode = mode  # marks simulation to be started in main thread
