''' Interface Elements needed for User Interaction '''

import pygame
import json
import numpy as np

import q100viz.keystone as keystone
import q100viz.session as session
from q100viz.devtools import devtools as devtools

############################ SLIDER ###################################


class Slider:
    def __init__(self, id):
        self.value = 0
        self.previous_value = 0
        self.idx = id
        self.bounding_box = pygame.Rect((0,0), (1,1))
        self.show_text = True  # display slider control text on grid
        self.show_controls = True

        self.color = pygame.Color(125, 125, 125)  # slider area
        self.alpha = 255
        self.handle = None
        self.previous_handle = None

        self.human_readable_value = {None: ''}
        for key in ['connection_to_heat_grid', 'refurbished', 'save_energy', 'global_connections']:
            self.human_readable_value[key] = ''
        self.human_readable_handle = {
            'connection_to_heat_grid': "Wärmenetzanschluss",
            'refurbished': "Sanierung",
            'save_energy': "Energie sparen",
            'game_stage': "Spielmodus",
            'num_connections': "zusätzliche Anschlüsse",
            'scenario_energy_prices': "Energiekostenszenario",
            None: "Slider-Funktion auswählen"
        }

    def process_value(self, force=False):
        ''' TODO: set up a struct (maybe csv) to import standard values >> this section should be automatized!
        e.g.
        if self.handle == 'name':
            session.environment['name'] = val_from_struct * slider_val
        '''
        if not force and self.value is self.previous_value or session.active_mode is session.modes['simulation']:
            return

        # household-specific:
        if self.handle == 'connection_to_heat_grid':
            session.buildings.df.at[self.idx,"connection_to_heat_grid"] = False if self.value <= 0.2 else int(np.interp((self.value), [0.2, 1], [session.min_connection_year, session.modes['simulation'].max_year]))
            self.human_readable_value['connection_to_heat_grid'] = "n.a." if self.value <= 0.2 else int(
                np.interp(float(self.value), [0.2, 1], [session.min_connection_year, session.modes['simulation'].max_year]))

        elif self.handle == 'refurbished':
            session.buildings.df.at[self.idx, 'refurbished'] = False if self.value <= 0.2 else int(np.interp((self.value), [0.2, 1], [session.min_refurb_year, session.modes['simulation'].max_year]))
            self.human_readable_value['refurbished'] = "n.a." if self.value <= 0.2 else int(
                np.interp(float(self.value), [0.2, 1], [session.min_refurb_year, session.modes['simulation'].max_year]))

        elif self.handle == 'save_energy':
            session.buildings.df.at[self.idx, 'save_energy'] = self.value > 0.5
            self.human_readable_value['save_energy'] = 'ja' if self.value > 0.5 else 'nein'
            
        elif self.handle == 'global_connections':
            session.buildings.connect_buildings_until_idx(int(self.value * len(session.buildings.df)))
            
        self.previous_value = self.value

    def update_handle(self, cell_handle, cell_id):
        if self.show_controls:
            self.handle = cell_handle
            self.process_value()  # update values
            self.group = cell_id
            if self.previous_handle is not self.handle:
                session.api.send_message(json.dumps({'sliders': {
                    "id": self.idx,
                    "handle": self.handle,
                    "group": self.group}}))
                self.previous_handle = self.handle
                
    def update_from_interaction(self, mouse_pos):
        # horizontal slider: w > h
        if self.bounding_box.width > self.bounding_box.height:
            self.value = (mouse_pos[0] - self.bounding_box.left) / self.bounding_box.width
        # vertical slider: w < h
        else:
            self.value = (mouse_pos[1] - self.bounding_box.top) / self.bounding_box.height
            
class RoundSlider(Slider):
    ''' 
    Round slider that is rotation-based.
    '''
    def process_value(self, force=False):
        '''
        Process self.value just like in a Slider object, but with different thresholds for the decisions.
        '''
        if not force and self.value is self.previous_value or session.active_mode is session.modes['simulation']:
            return
        print(self.value)

        # household-specific:
        if self.handle == 'connection_to_heat_grid':
            session.buildings.df.at[self.idx,"connection_to_heat_grid"] = False if self.value > 0.5 else int(np.interp((self.value), [0, 0.5], [session.min_connection_year, session.modes['simulation'].max_year]))
            self.human_readable_value['connection_to_heat_grid'] = "n.a." if self.value > 0.5 else int(
                np.interp(float(self.value), [0, 0.5], [session.min_connection_year, session.modes['simulation'].max_year]))

        elif self.handle == 'refurbished':
            session.buildings.df.at[self.idx, 'refurbished'] = False if self.value > 0.5 else int(np.interp((self.value), [0, 0.5], [session.min_refurb_year, session.modes['simulation'].max_year]))
            self.human_readable_value['refurbished'] = "n.a." if self.value > 0.5 else int(
                np.interp(float(self.value), [0, 0.5], [session.min_refurb_year, session.modes['simulation'].max_year]))

        elif self.handle == 'save_energy':
            session.buildings.df.at[self.idx, 'save_energy'] = self.value > 0.25 and self.value <= 0.75
            self.human_readable_value['save_energy'] = 'ja' if self.value > 0.25 and self.value <= 0.75 else 'nein'
            
        elif self.handle == 'global_connections':
            session.buildings.connect_buildings_until_idx(int(self.value * len(session.buildings.df)))
            
        self.previous_value = self.value