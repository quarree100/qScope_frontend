from pygame.locals import *
import pygame
import shapely

from config import *
import session


class EditMode:
    def __init__(self):
        self.polygon_selector = 0
        self.relevant_polygons = []

    def process_event(self, event):
        session.buildings.iloc[self.polygon_selector, 6] = True  # mark building as selected

        if event.type == KEYDOWN:
            if event.key == K_PLUS:
                self.polygon_selector = (self.polygon_selector + 1) % (len(session.buildings)-1)
                session.buildings.iloc[self.polygon_selector, 6] = True  # mark building as selected
                session.buildings.iloc[self.polygon_selector-1, 6] = False  # unselect previous

            elif event.key == K_MINUS:
                self.polygon_selector = (self.polygon_selector - 1) % (len(session.buildings)-1)
                session.buildings.iloc[self.polygon_selector, 6] = True  # mark building as selected
                session.buildings.iloc[self.polygon_selector+1, 6] = False  # unselect previous

            elif event.key == K_SPACE:
                self.relevant_polygons.append(session.buildings.index.values[self.polygon_selector])

            elif event.key in [K_UP, K_DOWN, K_LEFT, K_RIGHT]:
                polygon = session.buildings.iloc[self.polygon_selector, 0].exterior.coords
                points = []
                for pt in list(polygon):
                    # move all points in geometry towards desired direction:
                    point = shapely.geometry.Point(pt)
                    if event.key == K_UP:
                        points.append((point.x, point.y + 2))
                    elif event.key == K_DOWN:
                        points.append((point.x, point.y - 2))
                    elif event.key == K_LEFT:
                        points.append((point.x - 2, point.y))
                    elif event.key == K_RIGHT:
                        points.append((point.x + 2, point.y))

                session.buildings.iloc[self.polygon_selector, 0] = shapely.geometry.Polygon(points)
            
            elif event.key == K_s:
                session.buildings['geometry'].to_file(SAVED_BUILDINGS_FILE)
                print('saved buildings.shp to', SAVED_BUILDINGS_FILE)
                with open('export/relevant_polygons.txt', "w") as txt_file:
                    for osm_id in self.relevant_polygons:
                        txt_file.write(str(osm_id) + ",")

    def draw(self, canvas):
        if len(session.buildings[session.buildings.selected]):
            # highlight selected buildings
            session.gis.draw_polygon_layer(
                canvas,
                session.buildings[session.buildings.selected], 3, (255, 255, 255)
            )

        font = pygame.font.SysFont('Arial', 11, True, False)
        # mouse_x = pygame.mouse.get_pos()[0]
        # mouse_y = pygame.mouse.get_pos()[1]
        # text = font.render(str(mouse_x)+","+str(mouse_y), True, (255, 255, 255))
        text = font.render(str(session.buildings.index.values[self.polygon_selector]), True, (255, 255, 255))
        session.viewport.blit(text, (1500, 800))

        relevant_polygons_string = ""
        for snip in self.relevant_polygons:
            relevant_polygons_string = relevant_polygons_string + ", " + str(snip)
        text = font.render(relevant_polygons_string, True, (255, 255, 255))
        session.viewport.blit(text, (100, 800))

        # display num of buildings:
        text = font.render(str(self.polygon_selector % (len(session.buildings)-1)) + "/" + str(len(session.buildings)-2), True, (255, 255, 255))
        session.viewport.blit(text, (1500, 830))

