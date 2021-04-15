import cv2
import numpy


class CornerPinSurface:
    def __init__(self, points):
        """Load control points and calculate the transformation matrix."""
        src = numpy.float32([[0, 0], [width, 0], [width, height], [0, height]])
        dst = numpy.float32(points)

        self.transform = cv2.getPerspectiveTransform(src, dst)

    def get_transform_mat(self):
        """Return the transformation matrix as 4x4 matrix."""
        t = self.transform
        return [[t[0][0], t[0][1], 0, t[0][2]],
                [t[1][0], t[1][1], 0, t[1][2]],
                [      0,       0, 1,       0],
                [t[2][0], t[2][1], 0,       1]]
