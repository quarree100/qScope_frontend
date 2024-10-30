''' The Questionnaire Mode provides questions that are to be answered by the user in order to assess their mindset/positioning towards Renewable Energies and to evaluate their general acceptance of the project. '''

import pygame
import datetime
import shapely
import numpy

import q100viz.session as session

class DataViewIndividual_Mode():
    def __init__(self):
        self.name = 'individual_data_view'
        self.mode_token_selection_time = datetime.datetime.now()
        self.activation_buffer_time = 2  # seconds before simulation begins
        self.global_alpha = 0

    def activate(self):
        '''do not call! This function is automatically called in main loop. Instead, enable a mode by setting session.active_mode = session.[mode]'''

        session.environment['mode'] = self.name

        session.show_polygons = True
        session.show_basemap = True

        session.environment['active_user_focus_data'] = 0
        session.api.send_dict(session.environment)

        session.api.send_message_as_json(session.buildings.get_dict_with_api_wrapper())
        
        session.buildings.df['selected'] = False
        session.buildings.df.loc[session.buildings.df[session.buildings.df['group'] == session.environment['active_user_focus_data']].iloc[0].name, 'selected'] = True


    def process_event(self, event):
        if event.type != pygame.locals.MOUSEBUTTONDOWN:
            return
        
        buildings = session.buildings.df
        mouse_pos = pygame.mouse.get_pos()
        for idx, row in enumerate(buildings.index):
            if shapely.Point(mouse_pos).within(shapely.geometry.Polygon(buildings.loc[idx, 'polygon'])):

                if buildings.loc[idx, 'group'] >= 0:
                    # toggle selection
                    session.buildings.df['selected'] = False        
                    buildings.at[idx, 'selected'] = True
                    session.environment['active_user_focus_data'] = buildings.loc[idx, 'group']

    def process_grid_change(self):
        pass


    def draw(self, canvas):
        
        self.global_alpha = 30 + \
            abs(int(numpy.sin(pygame.time.get_ticks() / 1000) * 105))

        # mark selected building to show user focus      
        focused_bd = session.buildings.df[session.buildings.df['group'] == session.environment['active_user_focus_data']]
        if len(focused_bd) > 0:
            scaled_polygon = \
                shapely.geometry.Polygon(focused_bd['polygon'].iloc[0]).buffer(15)
            pygame.draw.polygon(
                canvas, 
                pygame.Color(255, 255, 255, self.global_alpha),
                [pnt for pnt in scaled_polygon.exterior.coords])
            

        # draw GIS layers:
        if session.show_polygons:
            session._gis.draw_linestring_layer(
                canvas, session._gis.nahwaermenetz, (217, 9, 9), 3)
            session._gis.draw_buildings_connections(
                session.buildings.df)  # draw lines to closest heat grid

            session._gis.draw_polygon_layer(
                surface=canvas, 
                df=session.buildings.df[(session.buildings.df['connection_to_heat_grid']) | (session.buildings.df['group'] >= 0)],
                stroke=0
                )
            
        # highlight group buildings (draws colored stroke on top)
        sel_buildings = session.buildings.df[
            session.buildings.df['group'] >= 0]
        for building in sel_buildings.to_dict('records'):
            fill_color = pygame.Color(
                session.user_colors[int(building['group'])])

            points = session._gis.surface.transform(
                building['geometry'].exterior.coords)
          
            pygame.draw.polygon(
                session._gis.surface, fill_color, points, 2)
            
        
                        
        return

        nrows = 22
        font = pygame.font.SysFont('Arial', 18)

        column = 17
        row = 11
        canvas.blit(font.render(
            "Quartiersdaten", True, pygame.Color(255,255,255)),
            (session.grid_2.rects_transformed[column+nrows*row][1][0][0] - 25,  # x
            session.grid_2.rects_transformed[column+nrows*row][1][0][1] + 10)  # y
        )

        column = 17
        row = 14
        font = pygame.font.SysFont('Arial', 14)
        canvas.blit(font.render(
            "Gebäudeinformation", True, pygame.Color(255,255,255)),
            (session.grid_2.rects_transformed[column+nrows*row][1][0][0] + 4,
             session.grid_2.rects_transformed[column+nrows*row][1][0][1])
        )

        column = 17
        row = 17
        font = pygame.font.SysFont('Arial', 18)
        canvas.blit(font.render(
            "Interaktion", True, pygame.Color(255,255,255)),
            (session.grid_2.rects_transformed[column+nrows*row][1][0][0] + 8,
             session.grid_2.rects_transformed[column+nrows*row][1][0][1] + 10)
        )

    def update(self):
        pass