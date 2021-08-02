from pygame.locals import KEYDOWN, K_TAB, K_UP, K_DOWN, K_LEFT, K_RIGHT, K_s
import shapely

import q100viz.session as session


class EditMode:
    def __init__(self):
        self.polygon_selector = 0

    def process_event(self, event, config):
        buildings_file = config['SAVED_BUILDINGS_FILE']

        session.buildings.iloc[self.polygon_selector, 6] = True  # mark building as selected

        if event.type == KEYDOWN:
            if event.key == K_TAB:
                self.polygon_selector = (self.polygon_selector + 1) % session.buildings.size
                session.buildings.iloc[self.polygon_selector, 6] = True  # mark building as selected
                session.buildings.iloc[self.polygon_selector-1, 6] = False  # unselect previous

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
                session.buildings['geometry'].to_file(buildings_file)
                print('saved buildings.shp to', buildings_file)

    def draw(self, canvas):
        if len(session.buildings[session.buildings.selected]):
            # highlight selected buildings
            session.gis.draw_polygon_layer(
                canvas,
                session.buildings[session.buildings.selected], 3, (255, 255, 255)
            )
