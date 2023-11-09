import pygame
from pygame.locals import KEYDOWN, K_TAB, K_UP, K_DOWN, K_LEFT, K_RIGHT, K_SPACE, K_s, K_1, K_2, K_3, K_4

import q100viz.session as session
from q100viz.settings.config import config

class CalibrationMode:
    def __init__(self):
        self.name = 'calibration'
        self.active_anchor = 0
        self.magnitude = 1

    def activate(self):
        pass

    def process_event(self, event):
        keystone_file = config['SAVED_KEYSTONE_FILE']

        if event.type == KEYDOWN:
            if event.key == K_1:
                self.active_anchor = 0
            elif event.key == K_2:
                self.active_anchor = 1
            elif event.key == K_3:
                self.active_anchor = 2
            elif event.key == K_4:
                self.active_anchor = 3

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
                session._gis.surface.calculate(session.viewport.transform_mat)

                for grid in (session.grid_1, session.grid_2):
                    grid.surface.calculate(session.viewport.transform_mat)
                    grid.transform()
                    for slider in grid.sliders.values():
                        slider.surface.calculate(session.viewport.transform_mat)
                        slider.transform()

                session.basemap.surface.calculate(session._gis.surface.transform_mat)
                session.basemap.warp()

            elif event.key == K_s:
                session.viewport.save(keystone_file)
                print("corner points saved in keystone.save")

    def process_grid_change(self):
        pass

    def update(self):
        pass

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
        fill_color = (255,0,0) if self.magnitude == 0.1 else (0,0,255)
        pygame.draw.line(session.viewport, fill_color, [p1[0], p1[1]], [p4[0], p4[1]], 2)
        pygame.draw.line(session.viewport, fill_color, [p1[0], p1[1]], [p2[0], p2[1]], 2)
        pygame.draw.line(session.viewport, fill_color, [p3[0], p3[1]], [p2[0], p2[1]], 2)
        pygame.draw.line(session.viewport, fill_color, [p3[0], p3[1]], [p4[0], p4[1]], 2)

        font = pygame.font.SysFont('Arial', 30)
        session.viewport.blit(
            font.render(
                "[1, 2, 3, 4]: choose corner \
                [s]: save corner points to keystone file",
                True, (255, 255, 255)),
                (500, 700)
                )
