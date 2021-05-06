import cv2
import numpy


class CornerPinSurface:
    def __init__(self, src_points, dst_points):
        """Calculate the transformation matrixes from source and destination points."""
        src = numpy.float32(src_points)
        dst = numpy.float32(dst_points)

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
        src = numpy.float32([points])
        dst = cv2.perspectiveTransform(src, self.transform_mat)
        return dst[0].tolist()

    def inverse_transform(self, points):
        """Transform a list of canvas points onto the surface."""
        src = numpy.float32([points])
        dst = cv2.perspectiveTransform(src, self.inverse_transform_mat)
        return dst[0].tolist()
