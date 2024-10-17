''' Interface Elements needed for User Interaction '''

import pygame
import json
import numpy as np

import q100viz.keystone as keystone
import q100viz.session as session
from q100viz.devtools import devtools as devtools
from q100viz.graphics.graphictools import Image

images = {
    'start_simulation': pygame.image.load("images/start_simulation.png"),
    'start_buildings_interaction': pygame.image.load("images/start_buildings_interaction.png"),
    'start_individual_data_view': pygame.image.load("images/start_individual_data_view.png"),
    'start_total_data_view': pygame.image.load("images/start_total_data_view.png"),
    'refurbished': pygame.image.load("images/refurbished.png"),
    'connection_to_heat_grid': pygame.image.load("images/connection_to_heat_grid.png"),
    'save_energy': pygame.image.load("images/save_energy.png"),
}

############################ SLIDER ###################################


class Slider:
    def __init__(self, canvas_size, id, coords, x_cell_range):
        self.value = 0
        self.previous_value = 0
        self.group = -1
        self.id = id  # unique STRING identifier for slider
        self.id_int = int(id[-1])
        self.show_text = True  # display slider control text on grid
        self.show_controls = True
        self.x_cell_range = x_cell_range  # limits of slider handles
        # cm

        self.color = pygame.Color(125, 125, 125)  # slider area
        self.alpha = 255
        self.handle = None
        self.previous_handle = None

        # this is used for the activation of the next question in questionnaire mode  # TODO: get slider position initially and set toggle accordingly (Slider should not "start at" this position)
        self.toggle_question = False

        # create rectangle around centerpoint:
        self.coords = coords
        self.surface = keystone.Surface(canvas_size, pygame.SRCALPHA)

        self.VALID_HANDLES = ['connection_to_heat_grid', 'refurbished',
                              'save_energy']

        self.human_readable_value = {None: ''}
        for key in self.VALID_HANDLES:
            self.human_readable_value[key] = ''
        self.human_readable_function = {
            'connection_to_heat_grid': "Wärmenetzanschluss",
            'refurbished': "Sanierung",
            'save_energy': "Energie sparen",
            'game_stage': "Spielmodus",
            'num_connections': "zusätzliche Anschlüsse",
            'scenario_energy_prices': "Energiekostenszenario",
            None: "Slider-Funktion auswählen"
        }

    def draw_controls(self, canvas=None):
        '''
        renders slider-selector texts (options) and tool tipps
        '''

        return
    # TODO: all the slider handling..
        # slider controls → set slider color
        # alpha value for unselected cells
        self.alpha = 100 + \
            abs(int(np.sin(pygame.time.get_ticks() / 1000) * 105))

        self.color = pygame.Color(0, 0, 0, 0)

        if self.show_controls:
            stroke = 0

            pygame.draw.polygon(
                self.surface, self.color, rect_points, stroke
            )

            # always draw globals:
            if cell.handle.__contains__("connections"):
                pygame.draw.polygon(
                    self.surface, self.color, rect_points, stroke)

        # icons:
        if cell.handle in ['connection_to_heat_grid', 'refurbished', 'save_energy'] and int(self.id[-1]) in session.buildings.df['group'].values:
            ncols = session.ncols
            # TODO: why does this have to be shifted ~4*cell_width to the left??
            x = self.grid.rects_transformed[cell.x +
                                            ncols*cell.y][1][3][0] - 185
            y = self.grid.rects_transformed[cell.x +
                                            ncols*cell.y][1][0][1] - 0
            # grey background color:
            pygame.draw.polygon(
                self.surface, (255, 255, 255, self.alpha), rect_points, 0)

            self.surface.blit(self.images[cell.handle].image, (x, y))

        handle_string = None
        # slider control texts:
        if self.show_text and int(self.id[-1]) in session.buildings.df['group'].values:
            font = pygame.font.SysFont('Arial', 10)
            if cell.handle == "connection_to_heat_grid":
                handle_string = "Anschluss"
            elif cell.handle == "refurbished":
                handle_string = "Sanierung"
            elif cell.handle == "save_energy":
                handle_string = "Energiesparen"

        # global icons:
        if cell.handle in ['start_simulation', 'start_individual_data_view', 'start_total_data_view', 'start_buildings_interaction']:
            ncols = session.ncols
            # TODO: why does this have to be shifted 4*cell_width to the left??
            x = self.grid.rects_transformed[cell.x +
                                            ncols*cell.y][1][3][0] - 185
            y = self.grid.rects_transformed[cell.x +
                                            ncols*cell.y][1][0][1] - 0
            # grey background color:
            pygame.draw.polygon(
                self.surface, (255, 255, 255, self.alpha), rect_points, 0)

            self.surface.blit(self.images[cell.handle].image, (x, y))

        # global texts:
        if self.show_text and cell.y == len(self.grid.grid) - 1:
            font = pygame.font.SysFont('Arial', 10)
            if cell.handle == "scenario_energy_prices":
                handle_string = "Energiepreise"
            if cell.handle == "num_connections":
                handle_string = "Anschlüsse"

        if handle_string is not None:
            self.surface.blit(
                font.render(handle_string, True, (255, 255, 255)),
                [rect_points[0][0], rect_points[0][1] + 35]
            )

        ###################### slider text: ###########################
        font = pygame.font.SysFont('Arial', 18)

        if self.show_text and int(self.id_int) in session.buildings.df['group'].values:

            # display human readable slider name:
            # string is either "function..........val" or "please select"
            if self.handle is not None:
                slider_text = str(self.human_readable_function[self.handle]) \
                    + "." * (40 - len(self.human_readable_function[self.handle])) \
                    + str(self.human_readable_value[self.handle])
            elif len(session.buildings.df[session.buildings.df['group'] == self.id_int].index) > 0:
                slider_text = session.buildings.df[session.buildings.df['group']
                                                   == self.id_int].iloc[0].address

            self.surface.blit(font.render(slider_text, True, (255, 255, 255)),
                              [self.coords_transformed[0][0], self.coords_transformed[0][1] - 20])

        if devtools.VERBOSE_MODE:
            self.surface.blit(font.render(str(self.value), True, (
                255, 255, 255)), (self.coords_transformed[3][0] - 20, self.coords_transformed[3][1]-20))

        canvas.blit(self.surface, (0, 0))

    def draw_area(self):
        '''
        draws option-specific layout onto the slider area.
        save_energy: red/[user_color] field for binary yes/no option
        connection/refurbishment: selection of specific year
        '''

        self.alpha = 100 + \
            abs(int(np.sin(pygame.time.get_ticks() / 1000) * 105))

        # draw slider handles if user has selected building:
        # user selected at least one building
        if not int(self.id[-1]) in session.buildings.df['group'].values:
            return
        # green field:
        c = self.coords
        points = [c[0], c[1], c[2], c[3]]
        points_transformed = self.surface.transform(points)
        pygame.draw.polygon(
            self.surface,
            pygame.Color(
                session.user_colors[int(self.id[-1])][0],
                session.user_colors[int(self.id[-1])][1],
                session.user_colors[int(self.id[-1])][2],
                self.alpha),
            points_transformed)

        ############# binary selection #############
        if self.handle == 'save_energy':
            pygame.draw.line(
                self.surface, pygame.Color(255, 255, 255), (self.coords_transformed[0][0] + (
                    self.coords_transformed[3][0] - self.coords_transformed[0][0]) / 2, self.coords_transformed[0][1] + 2),
                (self.coords_transformed[0][0] + (self.coords_transformed[3][0] - self.coords_transformed[0][0]) / 2, self.coords_transformed[1][1] + 2), width=2)

            # red field:
            c = self.coords
            points = [
                c[0],  # bottom left
                c[1],  # top left
                [c[2][0] - c[1][0]/2, c[2][1]],  # top right
                [c[3][0] - c[1][0]/2, c[3][1]]]  # bottom right
            points_transformed = self.surface.transform(points)
            pygame.draw.polygon(self.surface, pygame.Color(
                130, 20, 55), points_transformed)

            # user-color field:
            c = self.coords
            points = [
                [c[0][0] + (c[3][0] - c[0][0]) / 2, c[0][1]],  # bottom left
                [c[1][0] + (c[2][0] - c[1][0]) / 2, c[1][1]],  # top left
                c[2],  # top right
                c[3]]  # bottom right
            points_transformed = self.surface.transform(points)
            pygame.draw.polygon(
                self.surface, pygame.Color(
                    session.user_colors[int(self.id[-1])][0],
                    session.user_colors[int(self.id[-1])][1],
                    session.user_colors[int(self.id[-1])][2]),
                points_transformed)

        ############# year selection #############
        elif self.handle in ['connection_to_heat_grid', 'refurbished']:
            min_year = session.min_connection_year if self.handle == 'connection_to_heat_grid' else session.min_refurb_year
            max_year = session.simulation.max_year if self.handle == 'connection_to_heat_grid' else session.simulation.max_year

            x0 = self.coords_transformed[0][0]  # in px
            x3 = self.coords_transformed[3][0]  # in px
            y0 = self.coords_transformed[0][1]  # in px
            y1 = self.coords_transformed[1][1]  # in px
            y3 = self.coords_transformed[3][1]  # in px

            # physical slider area dimensions:
            s0 = x0 + (x3 - x0) * self.physical_diff_L / \
                self.physical_slider_area_length  # in px
            s1 = x0 + (x3 - x0) * self.physical_diff_R / \
                self.physical_slider_area_length  # in px

            # user-color field:
            c = self.coords
            points = [
                [c[0][0] + (c[3][0] - c[0][0]), c[0][1]],  # bottom left
                [c[1][0] + (c[2][0] - c[1][0]), c[1][1]],  # top left
                c[2],  # top right
                c[3]]  # bottom right
            points_transformed = self.surface.transform(points)
            pygame.draw.polygon(
                self.surface, pygame.Color(
                    session.user_colors[int(self.id[-1])][0],
                    session.user_colors[int(self.id[-1])][1],
                    session.user_colors[int(self.id[-1])][2]),
                points_transformed)

            # red field: no connection
            points = [
                (x0, y0),  # bottom left
                (x0, y1),  # top left
                (s0 + (s1 - s0) * 0.21, y1),  # top right
                (s0 + (s1 - s0) * 0.21, y0)  # bottom right
            ]

            pygame.draw.polygon(
                self.surface, pygame.Color(130, 20, 55), points)

            font = pygame.font.SysFont('Arial', 10)

            # intermediate seperators:
            for x in [0.2, 0.6, 1.0]:
                pygame.draw.line(
                    self.surface, pygame.Color(200, 200, 200),
                    (s0 + (s1 - s0) * x, y0 - 35),
                    (s0 + (s1 - s0) * x, y1 + 13), width=1
                )
                self.surface.blit(font.render(str(int(np.interp((x), [0.2, 1], [min_year, max_year]))), True, (
                    200, 200, 200)), ((s0 + (s1 - s0) * x) - 10, y0 - 35))

            if devtools.VERBOSE_MODE:
                self.surface.blit(font.render("L", True, (
                    255, 255, 255)), (s0, y3-20))
                self.surface.blit(font.render("|", True, (
                    255, 255, 255)), (s0 + (s1 - s0) * 0.2, y3-20))
                self.surface.blit(font.render("x", True, (
                    255, 255, 255)), ((s0 + (s1 - s0) * self.value) + 5, y3-80))
                self.surface.blit(font.render("R", True, (
                    255, 255, 255)), (s1, y3-20))

    def transform(self):
        self.coords_transformed = self.surface.transform(self.coords)

    def process_value(self):
        ''' TODO: set up a struct (maybe csv) to import standard values >> this section should be automatized!
        e.g.
        if self.handle == 'name':
            session.environment['name'] = val_from_struct * slider_val
        '''
        if self.value is self.previous_value or session.active_mode is session.simulation:
            return

        # household-specific:
        if self.handle == 'connection_to_heat_grid':
            session.buildings.df.loc[((
                session.buildings.df.selected == True) & (session.buildings.df.group == self.group)), 'connection_to_heat_grid'] = False if self.value <= 0.2 else int(np.interp((self.value), [0.2, 1], [session.min_connection_year, session.simulation.max_year]))
            self.human_readable_value['connection_to_heat_grid'] = "n.a." if self.value <= 0.2 else int(
                np.interp(float(self.value), [0.2, 1], [session.min_connection_year, session.simulation.max_year]))

        elif self.handle == 'refurbished':
            session.buildings.df.loc[((
                session.buildings.df.selected == True) & (session.buildings.df.group == self.group)), 'refurbished'] = False if self.value <= 0.2 else int(np.interp((self.value), [0.2, 1], [session.min_refurb_year, session.simulation.max_year]))
            self.human_readable_value['refurbished'] = "n.a." if self.value <= 0.2 else int(
                np.interp(float(self.value), [0.2, 1], [session.min_refurb_year, session.simulation.max_year]))

        elif self.handle == 'save_energy':
            session.buildings.df.loc[(
                session.buildings.df.selected == True) & (session.buildings.df.group == self.group), 'save_energy'] = self.value > 0.5
            self.human_readable_value['save_energy'] = 'ja' if self.value > 0.5 else 'nein'

        session.api.send_message(json.dumps(session.environment))
        session.api.send_message(json.dumps(
            session.buildings.get_dict_with_api_wrapper()))

        self.previous_value = self.value

    def update_handle(self, cell_handle, cell_id):
        if self.show_controls:
            self.handle = cell_handle
            self.process_value()  # update values
            self.group = cell_id
            if self.previous_handle is not self.handle:
                session.api.send_message(json.dumps({'sliders': {
                    "id": self.id,
                    "handle": self.handle,
                    "group": self.group}}))
                self.previous_handle = self.handle


class MousePosition:
    def __init__(self, canvas_size):
        self.surface = keystone.Surface(canvas_size, pygame.SRCALPHA)

    def draw(self, surface, x, y):
        pygame.draw.circle(surface, pygame.color.Color(
            50, 160, 123), (x, y), 20)


class PopupMenu:
    def __init__(self, surface, origin=(0, 0), rect_dim=(100, 30), displace=(0, 0), menu_type=""):

        self.surface = surface

        self.origin = origin
        self.rect_width = rect_dim[0]
        self.rect_height = rect_dim[1]
        self.rect = pygame.Rect(origin[0], origin[1], rect_dim[0], rect_dim[1])
        self.displace = displace

        self.menu_type = menu_type
        self.alpha = 0
        self.color = pygame.Color(120, 130, 240)  # TODO: use user colors

        if self.menu_type == "decisions":

            img_max_w = 0
            img_max_h = 0
            for key in "connection_to_heat_grid", "refurbished", "save_energy":
                img_max_w = images[key].width if images[key].width > img_max_w else img_max_w
                img_max_h = images[key].height if images[key].height > img_max_h else img_max_h

            num_of_images = 3
            self.rect = pygame.Rect(
                self.origin[0], self.origin[1],
                num_of_images * img_max_w + num_of_images-1,
                img_max_h)

        # center rectangle:
        self.rect = self.rect.move(
            displace[0] - self.rect.width / 2,
            displace[1] - self.rect.height / 2)

    def draw(self):
        if self.alpha < 255:
            self.alpha = min(self.alpha + 75, 255)

        if (self.displace[0] is not 0 or self.displace[1] is not 0):
            pygame.draw.line(
                self.surface,
                pygame.Color(
                    self.color.r,
                    self.color.g,
                    self.color.b,
                    self.alpha),
                self.origin, self.rect.center, 2
            )

        if self.menu_type == "decisions":
            self.draw_decisions()

    def draw_decisions(self):

        pygame.draw.rect(
            surface=self.surface,
            color=pygame.Color(
                self.color.r,
                self.color.g,
                self.color.b,
                self.alpha),
            rect=self.rect.scale_by(1.2)
        )
        pygame.draw.rect(
            surface=self.surface,
            color=pygame.Color(255, 255, 255, self.alpha),
            rect=self.rect
        )

        i = 0
        for key in "connection_to_heat_grid", "refurbished", "save_energy":
            self.surface.blit(
                images[key],
                (self.rect.left + i * images[key].width,
                 self.rect.top)
            )
            i += 1
