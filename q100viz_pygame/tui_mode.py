import session


class TuiMode:
    def process_event(self, event):
        pass

    def draw(self, canvas):
        session.buildings['selected'] = False

        # process grid changes
        for grid in [session.grid_1, session.grid_2]:
            for y, row in enumerate(grid.grid):
                for x, cell in enumerate(row):
                    # find buildings intersecting with selected cell
                    if cell.selected:
                        # get viewport coordinates of the cell rectangle
                        cell_vertices = grid.surface.transform(
                            [[_x, _y] for _x, _y in [[x, y], [x + 1, y], [x + 1, y + 1], [x, y + 1]]]
                        )
                        ii = session.gis.get_intersection_indexer(session.buildings, cell_vertices)
                        session.buildings.loc[ii, 'selected'] = True
                        session.buildings.loc[ii, 'cell'] = f"{x},{y}"

        if len(session.buildings[session.buildings.selected]):
            # highlight selected buildings
            session.gis.draw_polygon_layer(
                canvas,
                session.buildings[session.buildings.selected], 2, (255, 0, 127)
            )
