import pygame
from pygame.locals import *

from config import *
import session


class CalibrationMode:
    def __init__(self):
        self.active_anchor = 0

    def process_event(self, event):
        if event.type == KEYDOWN:
            if event.key == K_TAB:
                self.active_anchor = 0 if self.active_anchor == 3 else self.active_anchor + 1
            elif event.key in [K_UP, K_DOWN, K_RIGHT, K_LEFT]:
                session.viewport.src_points[self.active_anchor][0] += 1 * (event.key == K_LEFT) - 1 * (event.key == K_RIGHT)
                session.viewport.src_points[self.active_anchor][1] += 1 * (event.key == K_UP) - 1 * (event.key == K_DOWN)

                # recalculate all surface projections
                session.viewport.calculate()
                session.gis.surface.calculate(session.viewport.transform_mat)
                session.grid_1.surface.calculate(session.viewport.transform_mat)
                session.grid_2.surface.calculate(session.viewport.transform_mat)
                session.basemap.surface.calculate(session.gis.surface.transform_mat)
                session.basemap.warp(canvas_size)
            elif event.key == K_s:
                session.viewport.save(SAVED_KEYSTONE_FILE)

    def draw(self, canvas):
        # draw calibration anchors
        for i, anchor in enumerate(session.viewport.transform([[0, 0], [0, 100], [100, 100], [100, 0]])):
            pygame.draw.rect(session.viewport, (255, 255, 255),
                             [anchor[0] - 10, anchor[1] - 10, 20, 20],
                             i != self.active_anchor)
