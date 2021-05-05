import cv2
import numpy


class CornerPinSurface:
    def __init__(self, points):
        """Load control points and calculate the transformation matrix."""
        src = numpy.float32([[0, 0], [width, 0], [width, height], [0, height]])
        dst = numpy.float32(points)

        self.transform_mat = cv2.getPerspectiveTransform(src, dst)
        self.inverse_transform_mat = numpy.linalg.inv(self.transform_mat)

    def get_transform_mat(self):
        """Return the transformation matrix as 4x4 matrix."""
        t = self.transform_mat
        return [[t[0][0], t[0][1], 0, t[0][2]],
                [t[1][0], t[1][1], 0, t[1][2]],
                [      0,       0, 1,       0],
                [t[2][0], t[2][1], 0,       1]]

    def transform(self, points):
        """Transform a list of surface points onto the canvas."""
        return cv2.perspectiveTransform(numpy.float32([points]), self.transform_mat)[0]

    def inverse_transform(self, points):
        """Transform a list of canvas points onto the surface."""
        return cv2.perspectiveTransform(numpy.float32([points]), self.inverse_transform_mat)[0]

    def inverse_transform_unit(self, points):
        """Transform a list of canvas points onto the normalized surface."""
        return [[x / width, y / height] for x, y in self.inverse_transform(points)]
