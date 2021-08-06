import pygame
from pygame.locals import KEYDOWN, K_TAB, K_UP, K_DOWN, K_LEFT, K_RIGHT, K_SPACE, K_s

import q100viz.session as session


class CalibrationMode:
    def __init__(self):
        self.active_anchor = 0
        self.magnitude = 1

    def process_event(self, event, config):
        keystone_file = config['SAVED_KEYSTONE_FILE']

        if event.type == KEYDOWN:
            if event.key == K_TAB:
                self.active_anchor = 0 if self.active_anchor == 3 else self.active_anchor + 1
            elif event.key == K_SPACE:
                self.magnitude = 0.1 if (self.magnitude == 1) else 1
                print("magnitude = ", self.magnitude)
            elif event.key in [K_UP, K_DOWN, K_RIGHT, K_LEFT]:
                session.viewport.src_points[self.active_anchor][0] += (
                    self.magnitude * (event.key == K_LEFT) - self.magnitude * (event.key == K_RIGHT)
                )
                session.viewport.src_points[self.active_anchor][1] += (
                    self.magnitude * (event.key == K_UP) - self.magnitude * (event.key == K_DOWN)
                )

                # recalculate all surface projections
                session.viewport.calculate()
                session.gis.surface.calculate(session.viewport.transform_mat)
                session.grid_1.surface.calculate(session.viewport.transform_mat)
                session.grid_2.surface.calculate(session.viewport.transform_mat)
                session.basemap.surface.calculate(session.gis.surface.transform_mat)
                session.basemap.warp()
            elif event.key == K_s:
                session.viewport.save(keystone_file)

    def draw(self, canvas):
        # draw calibration anchors
        for i, anchor in enumerate(session.viewport.transform([[0, 0], [0, 100], [100, 100], [100, 0]])):
            pygame.draw.rect(session.viewport,
                             (255, 255, 255),
                             [anchor[0] - 10, anchor[1] - 10, 20, 20],
                             i != self.active_anchor)
