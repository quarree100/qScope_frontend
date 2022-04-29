import pygame
import pandas as pd

import q100viz.keystone as keystone
import q100viz.session as session
import q100viz.stats as stats
from config import config

class DataView:
    def __init__(self):
        pass


    def activate(self):
        pass

    def process_event(self):
        if event.type == pygame.locals.MOUSEBUTTONDOWN:
            session.grid_1.mouse_pressed(event.button)
            session.grid_2.mouse_pressed(event.button)
            session.flag_export_canvas = True

            self.process_grid_change()

    def process_grid_change(self):
        # process grid changes
        for grid in [session.grid_1, session.grid_2]:
            for y, row in enumerate(grid.grid):
                for x, cell in enumerate(row):
                    if cell.selected:
                        pass

        session.stats.send_simplified_dataframe_with_environment_variables(session.buildings[session.buildings.selected], session.environment)

    def draw(self):
        pass