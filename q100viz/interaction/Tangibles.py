import numpy
import shapely
import pygame

from pythontuio import TuioListener, Cursor, Object

import q100viz.session as session
from q100viz.devtools import devtools
from q100viz.settings.config import config
from q100viz.interaction.PopupMenu import TangibleMenu

class Tuio_Listener(TuioListener):

    def add_tuio_cursor(self, cursor: Cursor):
        devtools.print_verbose(
            f"Neuer Cursor hinzugefügt: ID={cursor.session_id}, X={cursor.position[0]}, Y={cursor.position[1]}")

    def update_tuio_cursor(self, cursor: Cursor):
        devtools.print_verbose(f"Cursor aktualisiert: ID={cursor.session_id}, X={cursor.position[0]}, Y={cursor.position[1]}")
        # devtools.print_verbose(cursor.get_message())

    def remove_tuio_cursor(self, cursor: Cursor):
        devtools.print_verbose(f"Cursor entfernt: ID={cursor.session_id}")

    def add_tuio_object(self, object: Object):
        devtools.print_verbose(
            f"Neues Tangible hinzugefügt: ID={object.class_id}, X={object.position[0]}, Y={object.position[1]}"
            )

        if object.class_id >= 0: 
            session.tangibles[object.class_id] = Tangible(object)

    def update_tuio_object(self, object: Object):
        # devtools.print_verbose(f"Object aktualisiert: ID={object.class_id}, X={object.position[0]}, Y={object.position[1]}, angle={object.angle}")
        # devtools.print_verbose(object.get_message())
        if object.class_id < 0: return
        if not object.class_id in session.tangibles.keys():
            session.tangibles[object.class_id] = Tangible(object)
        session.tangibles[object.class_id].update(object)

    def remove_tuio_object(self, object: Object):
        devtools.print_verbose(
            f"Object entfernt: ID={object.class_id}"
            )
        if not session.tangibles[object.class_id]: return

        session.tangibles[object.class_id].destroy()

class Tangible:
    def __init__(self, object):
        self.surface = pygame.Surface((500, 500), pygame.SRCALPHA).convert_alpha()
        self.bounding_box = pygame.Rect(0,0, self.surface.get_width(), self.surface.get_height())
        self.sel_idx = None  # index of currently selected building

        self.update(object)

    def update(self, object):

        self.id = object.class_id
        self.position = (
            object.position[0] * config['CANVAS_SIZE'][0],
            object.position[1] * config['CANVAS_SIZE'][1]
        )

        self.angle = numpy.rad2deg(object.angle)
        self.process_event()
        
        # update rotation of popup:
        if not self.sel_idx: return
        session.popup_menus[self.sel_idx].current_rotation = session.popup_menus[self.sel_idx].start_rotation + self.angle
        devtools.print_verbose(session.popup_menus[self.sel_idx].current_rotation)

    def draw(self, canvas):
        pass
    
    def draw_verbose(self, canvas):
        self.surface.fill((0,0,0,0))

        cx, cy = self.bounding_box.center
        
        pygame.draw.circle(
            surface=self.surface,
            color=pygame.Color(255, 255, 255),
            center=self.surface.get_rect().center,
            radius=20,
            width=1
        )

        pygame.draw.line(
            self.surface,
            (255, 255, 255),
            start_pos=(cx - 20, cy),
            end_pos=(cx + 20, cy)
        )
        pygame.draw.line(
            self.surface,
            (255, 255, 255),
            start_pos=(cx, cy + 20),
            end_pos=(cx, cy - 20)
        )

        font = pygame.font.SysFont('Arial', 16)
        text = font.render(
            f"ID {self.id}: ({int(self.position[0])}, {int(self.position[1])}) | r: {int(self.angle)}°", True, pygame.Color(255, 255, 255))
        
        self.surface.blit(text, (cx, cy))

        rotated = pygame.transform.rotate(self.surface, -self.angle)
        pos = rotated.get_rect(center = self.surface.get_rect(center = self.position).center)
        canvas.blit(rotated, pos)

    def process_event(self):
        buildings = session.buildings.df
        if self.sel_idx:
            # leave:
            if not shapely.Point(self.position).within(shapely.geometry.Polygon(buildings.loc[self.sel_idx, 'polygon'])):
                buildings.at[self.sel_idx, 'selected'] = False
                buildings.at[self.sel_idx, 'group'] = -1
                session.popup_menus[self.sel_idx].destroy()
                self.sel_idx = None
                return
            else:
                return
        
        # building selected:
        for idx, row in enumerate(buildings.index):
            if shapely.Point(self.position).within(shapely.geometry.Polygon(buildings.loc[idx, 'polygon'])):
                self.sel_idx = idx

                buildings.at[idx, 'selected'] = True
                buildings.at[idx, 'group'] = self.id % 4
                centroid = shapely.geometry.Polygon(
                    buildings.loc[idx, 'polygon']).centroid.coords[0]
                popup = TangibleMenu(
                    session.viewport,
                    centroid,
                    displace=(0, 200),
                    idx=idx,
                    start_rotation=self.angle
                )
                
                return

    def destroy(self):
        if self.sel_idx:
            session.buildings.df.at[self.sel_idx, 'selected'] = False
            session.buildings.df.at[self.sel_idx, 'group'] = -1
            session.buildings.df.loc[self.sel_idx, 'popup'].destroy()
        del session.tangibles[self.id]