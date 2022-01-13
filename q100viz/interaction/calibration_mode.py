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
                    self.magnitude * (event.key == K_LEFT) - self.magnitude * (
                        event.key == K_RIGHT)
                )
                session.viewport.src_points[self.active_anchor][1] += (
                    self.magnitude * (event.key == K_UP) - self.magnitude * (event.key == K_DOWN)
                )

                # recalculate all surface projections
                session.viewport.calculate()
                session.gis.surface.calculate(session.viewport.transform_mat)

                session.grid_1.surface.calculate(session.viewport.transform_mat)
                session.grid_1.transform()

                session.grid_2.surface.calculate(session.viewport.transform_mat)
                session.grid_2.transform()

                session.basemap.surface.calculate(session.gis.surface.transform_mat)
                session.basemap.warp()

                session.slider.surface.calculate(session.viewport.transform_mat)
                session.slider.transform()
            elif event.key == K_s:
                session.viewport.save(keystone_file)

    def draw(self, canvas):
        # draw calibration anchors
        for i, anchor in enumerate(
                session.viewport.transform([[0, 0], [0, 100], [100, 100], [100, 0]])):
            pygame.draw.rect(session.viewport,
                             (255, 255, 255),
                             [anchor[0] - 10, anchor[1] - 10, 20, 20],
                             i != self.active_anchor)

        # connect anchor points with lines
        p1, p2, p3, p4 = session.viewport.transform([[0, 0], [0, 100], [100, 100], [100, 0]])
        fill_color = (255,0,0) if self.magnitude == 1 else (0,0,255)
        pygame.draw.line(session.viewport, fill_color, [p1[0], p1[1]], [p4[0], p4[1]], 2)
        pygame.draw.line(session.viewport, fill_color, [p1[0], p1[1]], [p2[0], p2[1]], 2)
        pygame.draw.line(session.viewport, fill_color, [p3[0], p3[1]], [p2[0], p2[1]], 2)
        pygame.draw.line(session.viewport, fill_color, [p3[0], p3[1]], [p4[0], p4[1]], 2)
