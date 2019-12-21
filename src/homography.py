import cv2
import numpy as np
import sys
import utils
from matplotlib import pyplot as plt
import math
import utils

if __name__ == '__main__':
    img = cv2.imread('../img/football1.jpg')
    field = utils.GetFieldLayer(img)
    cv2.imshow("Field Layer",field)
    field = cv2.GaussianBlur(field, (3, 3), cv2.BORDER_DEFAULT)
    edges = cv2.Canny(field, 100, 300)
    lines = cv2.HoughLines(edges, 1, np.pi / 180, 150, None, 0, 0)

    if lines is not None:
        for i in range(0, len(lines)):
            rho = lines[i][0][0]
            theta = lines[i][0][1]
            a = math.cos(theta)
            b = math.sin(theta)
            x0 = a * rho
            y0 = b * rho
            pt1 = (int(x0 + 1000*(-b)), int(y0 + 1000*(a)))
            pt2 = (int(x0 - 1000*(-b)), int(y0 - 1000*(a)))
            cv2.line(img, pt1, pt2, (0,0,255), 1,cv2.LINE_AA)

    cv2.imshow("Canny Result",edges)
    cv2.imshow("Canny -> Houghlines",img)
    cv2.waitKey(0)
