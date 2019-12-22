import cv2
import math
import utils
import numpy as np

class Line:
    def __init__(self, pt1, pt2):
        self.pt1 = pt1
        self.pt2 = pt2
        self.dx = pt2[0] - pt1[0]
        self.dy = pt2[1] - pt1[1]
        self.m = self.dy / self.dx
        self.b = pt1[1] - self.m * pt1[0]

    def intersection(self, other):
        x = (other.b - self.b) / (self.m - other.m)
        y = self.m * x + self.b
        return (int(x), int(y))


if __name__ == '__main__':
    img = cv2.imread('../img/football1.jpg')
    field = utils.GetFieldLayer(img)
    # cv2.imshow("Field Layer", field)
    field = cv2.GaussianBlur(field, (3, 3), cv2.BORDER_DEFAULT)
    edges = cv2.Canny(field, 100, 300)
    lines = cv2.HoughLines(edges, 1, math.radians(1.7), 150, None, 0, 0)

    lns = []

    if lines is not None:
        for i in range(0, len(lines)):
            rho = lines[i][0][0]
            theta = lines[i][0][1]
            a = math.cos(theta)
            b = math.sin(theta)
            x0 = a * rho
            y0 = b * rho
            pt1 = (int(x0 + 1000 * (-b)), int(y0 + 1000 * (a)))
            pt2 = (int(x0 - 1000 * (-b)), int(y0 - 1000 * (a)))
            lns.append(Line(pt1, pt2))

    # Calculate intersection points
    intersections = []
    for i in range(0, len(lns)):
        for j in range(i + 1, len(lns)):
            point = lns[i].intersection(lns[j])
            intersections.append(point)
        cv2.line(img, lns[i].pt1, lns[i].pt2, (0, 0, 255), 1)


    # Cleanup similar points and points outside of the image
    i = 0
    while i < len(intersections):

        # Check if outside of image
        xi,yi = intersections[i]
        sy,sx,_ = img.shape
        if xi < 0 or yi < 0 or xi > sx or yi > sy:
            del intersections[i]
            continue

        # Check if similar 
        j = i+1
        while j < len(intersections):
            distance = np.linalg.norm(list(x-y for x,y in zip(intersections[i],intersections[j])))
            if distance < 20:
                del intersections[j]
                continue
            j += 1
        i += 1

    # Draw points
    for point in intersections:
        cv2.circle(img, point, 10, (0, 255, 0))

    # cv2.imshow("Canny Result", edges)
    cv2.imshow("Canny -> Houghlines", img)
    cv2.waitKey(0)
