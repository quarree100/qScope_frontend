import pygame
import numpy as np
from q100viz.settings.config import config
import q100viz.session as session
import q100viz.graphics.graphictools as graphictools
import q100viz.graphics.colors as colors

def year_selection(popup):
    
    graphictools.draw_pie(
        popup.surface,
        pygame.Color(
            popup.colors["user"].r,
            popup.colors["user"].g,
            popup.colors["user"].b,
            popup.alpha),
        popup.origin,
        popup.radius,
        0, 180, 0.1
    )
    
    num_of_years = session.modes['simulation'].max_year - config['SIMULATION_FORCE_START_YEAR']
    divisions = 5 if num_of_years > 20 else 2
    
    # year ticks:
    graphictools.draw_pie(
        popup.surface,
        pygame.Color("white"),
        popup.origin,
        popup.radius,
        0, 180, (180 / divisions), 1
    )            
    
    # display year string:
    rot = 180
    for year in range(config['SIMULATION_FORCE_START_YEAR'], session.modes['simulation'].max_year + divisions, divisions):
        
        if year > (config['SIMULATION_FORCE_START_YEAR'] + num_of_years / 2):
            graphictools.shadow_text(
                    text=str(year), 
                    surface=popup.surface, 
                    position=(popup.origin[0] + np.cos(np.deg2rad(rot)) * popup.radius,
                              popup.origin[1] + np.sin(np.deg2rad(rot)) * popup.radius), 
                    align='topleft', 
                    font_type='Arial', font_size=20)
        else:
            graphictools.shadow_text(
                    text=str(year), 
                    surface=popup.surface, 
                    position=(popup.origin[0] + np.cos(np.deg2rad(rot)) * popup.radius,
                              popup.origin[1] + np.sin(np.deg2rad(rot)) * popup.radius), 
                    align='topright', 
                    font_type='Arial', font_size=20)

        rot -= (180 / divisions)
        
    # final year:    
                    
    pygame.draw.line(
        popup.surface,
        pygame.Color(255,255,255),
        (popup.origin[0] + np.cos(np.deg2rad(180)) * 40 * 0.7,
        popup.origin[1] + np.sin(np.deg2rad(180)) * 40 * 0.7),
        (popup.origin[0] + np.cos(np.deg2rad(180)) * 80,
        popup.origin[1] + np.sin(np.deg2rad(180)) * 80),
        1
    )
    
    rotation_line(popup=popup)
    handle_information(popup=popup)

            
def toggle(popup):
    graphictools.draw_pie(
    popup.surface,
    pygame.Color(
            popup.colors["user"].r,
            popup.colors["user"].g,
            popup.colors["user"].b,
            popup.alpha),
    popup.origin,
    popup.radius,
    90, 270, 0.1
    )
        
    rotation_line(popup=popup)
    handle_information(popup=popup)

def rotation_line(popup):
    # rotation line:
    pygame.draw.line(
        popup.surface,
        pygame.Color(popup.colors["user"]),
        (popup.origin[0] + np.cos(np.deg2rad(popup.current_rotation)) * 20 * 0.7,
        popup.origin[1] + np.sin(np.deg2rad(popup.current_rotation)) * 20 * 0.7),
        (popup.origin[0] + np.cos(np.deg2rad(popup.current_rotation)) * popup.radius * 1.25,
        popup.origin[1] + np.sin(np.deg2rad(popup.current_rotation)) * popup.radius * 1.25),
        6
    )
    
def handle_information(popup):
    
    graphictools.shadow_text(
        text=f"{str(popup.slider.human_readable_handle[popup.slider.handle])}: {str(popup.slider.human_readable_value[popup.slider.handle])}", 
        surface=popup.surface, 
        position=(
            popup.origin[0], 
            popup.origin[1] + popup.radius * 1.2), 
        align='center', 
        font_type='Arial', font_size=20)
        
def select_user(canvas, icons):
    for i in range(session.num_of_users):  # TODO: use only user-selected buildings, so focusing "no building" will not be an option here
        
        origin = icons['start_individual_data_view'].rect.center
        radius = icons['start_individual_data_view'].rect.scale_by(1.3).width / 2
        
        graphictools.draw_pie(
            canvas, 
            colors.user_colors[i], 
            origin, 
            radius=radius, 
            start_angle=i * 360 / session.num_of_users, 
            stop_angle=i * 360 / session.num_of_users + 360 / session.num_of_users, 
            step=0.1)

    x = origin[0] + np.cos(np.deg2rad(icons['start_individual_data_view'].magnitude * 360)) * radius * 1.25
    y = origin[1] + np.sin(np.deg2rad(icons['start_individual_data_view'].magnitude * 360)) * radius * 1.25

    pygame.draw.line(
        canvas, pygame.Color("white"),
        origin, (x, y), 4
    )