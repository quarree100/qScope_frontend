import numpy
import shapely
import pygame

import pythontuio

import q100viz.session as session
from q100viz.devtools import devtools
from q100viz.settings.config import config
from q100viz.interaction.PopupMenu import TangibleMenu

class Tuio_Listener(pythontuio.TuioListener):

    def add_tuio_cursor(self, cursor: pythontuio.Cursor):
        devtools.print_verbose(
            f"Neuer Cursor hinzugefügt: ID={cursor.session_id}, X={cursor.position[0]}, Y={cursor.position[1]}")
        session.frontend.handle_mouse_down(cursor.position)
        session.tangibles['cursor'] = Cursor(cursor)
        session.frontend.handle_mouse_down(session.tangibles['cursor'].position)

    def update_tuio_cursor(self, cursor: pythontuio.Cursor):
        devtools.print_verbose(
            f"Cursor aktualisiert: ID={cursor.session_id}, X={cursor.position[0]}, Y={cursor.position[1]}"
            )
        session.tangibles['cursor'].update(cursor)
        # session.frontend.handle_mouse_motion(session.tangibles['cursor'].position)

    def remove_tuio_cursor(self, cursor: pythontuio.Cursor):
        devtools.print_verbose(f"Cursor entfernt: ID={cursor.session_id}")
        session.frontend.handle_mouse_up(cursor.position)
        session.frontend.handle_mouse_up(session.tangibles['cursor'].position)
        session.tangibles['cursor'].destroy()

    def add_tuio_object(self, object: pythontuio.Object):
        devtools.print_verbose(
            f"Neues Tangible hinzugefügt: ID={object.class_id}, X={object.position[0]}, Y={object.position[1]}"
            )

        if object.class_id >= 0:
            session.tangibles[object.class_id] = Tangible(object)

    def update_tuio_object(self, object: pythontuio.Object):
        # devtools.print_verbose(f"pythontuio.Object aktualisiert: ID={object.class_id}, X={object.position[0]}, Y={object.position[1]}, angle={object.angle}")
        # devtools.print_verbose(object.get_message())

        if object.class_id < 0: return

        # create object if tangible was already on surface:
        if not object.class_id in session.tangibles.keys():
            session.tangibles[object.class_id] = Tangible(object)

        session.tangibles[object.class_id].update(object)

    def remove_tuio_object(self, object: pythontuio.Object):
        devtools.print_verbose(
            f"pythontuio.Object entfernt: ID={object.class_id}"
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
        
        session.active_mode.process_tangible_event(self.id, self.position, self.angle)
        session.frontend.side_panel.handle_mouse_motion(self.position)
        session.frontend.side_panel.process_rotation(self.position, self.angle)

        # update rotation of popup:
        if not self.id in list(session.buildings.df['tangible'].values): return
        for idx in session.buildings.df.index:
            if session.buildings.df.loc[idx, 'tangible'] == self.id:
                session.buildings.df.loc[idx, 'popup'].process_rotation(self.angle)
                session.buildings.df.loc[idx, 'popup'].process_motion(self.position)
                        
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

    def destroy(self):
        if self.sel_idx:
            session.buildings.df.at[self.sel_idx, 'selected'] = False
            session.buildings.df.at[self.sel_idx, 'group'] = -1
            session.buildings.df.loc[self.sel_idx, 'popup'].destroy()
        del self


class Cursor(Tangible):

    def __init__(self, object):
        self.surface = pygame.Surface((500, 500), pygame.SRCALPHA).convert_alpha()
        self.bounding_box = pygame.Rect(0,0, self.surface.get_width(), self.surface.get_height())
        self.sel_idx = None  # index of currently selected building

        self.update(object)

    def update(self, cursor):

        self.id = cursor.session_id
        self.position = (
            cursor.position[0] * config['CANVAS_SIZE'][0],
            cursor.position[1] * config['CANVAS_SIZE'][1]
        )

        self.angle = 0
        self.process_event()

    def process_event(self):
        pass