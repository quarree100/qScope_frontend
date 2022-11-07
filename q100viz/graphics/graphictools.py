import cv2
import pygame

import q100viz.keystone as keystone

class Image():
    def __init__(self, file, canvas_size, viewport):
        self.file = file
        self.surface = keystone.Surface(canvas_size)

        self.img_h, self.img_w, _ = cv2.imread(file).shape

        # calculate the projection matrix (image pixels -> EPSG:3857)
        self.surface.src_points = [[0, 0], [0, self.img_h], [self.img_w, self.img_h], [self.img_w, 0]]

        x_2 = self.img_w/canvas_size[0] * 100
        y_2 = self.img_h/canvas_size[1] * 100
        self.surface.dst_points = [[0, 0], [0, y_2], [x_2, y_2], [x_2, 0]]
        self.surface.calculate(viewport.transform_mat)

    def warp(self, canvas_size):
        # warp image and update the surface
        image = self.surface.warp_image(self.file, canvas_size)
        self.image = pygame.image.frombuffer(image, image.shape[1::-1], 'BGR')
        self.image.set_colorkey((0, 0, 0))