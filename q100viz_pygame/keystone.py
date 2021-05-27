import cv2
import numpy
import pygame


class Surface(pygame.Surface):
    def calculate(self):
        """Calculate the transformation matrixes from source and destination points."""
        src = numpy.float32(self.src_points)
        dst = numpy.float32(self.dst_points)

        self.transform_mat = cv2.getPerspectiveTransform(src, dst)
        # self.inverse_transform_mat = numpy.linalg.inv(self.transform_mat)

    def transform(self, points):
        """Transform a list of surface points onto the canvas."""
        src = numpy.float32([points])
        dst = cv2.perspectiveTransform(src, self.transform_mat)
        return dst[0].tolist()

    def warp_image(self, file, dsize):
        img = cv2.imread(file)
        return cv2.warpPerspective(img, self.transform_mat, dsize)
