import cv2
import math
import utils
import numpy as np
from itertools import permutations

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


def findBestHomography():
    # Loop through all the possible permutations of 4 points in the image
    all_img_pts = [np.array(i, dtype=float) for i in intersections]
    for img_pts in permutations(intersections, 4):
        # Optimization: check if polygon is convex and clockwise
        if not utils.isConvex(img_pts) or not utils.isClockwise(img_pts):
            continue

        # Loop through all the possible permutations of 4 points in the reference
        for ref_points in permutations(utils.reference_points, 4):
            # Optimization: check if polygon is convex and clockwise
            if not utils.isConvex(img_pts) or not utils.isClockwise(img_pts):
                continue

            # Convert to np.ndarray of np.ndarray of float64
            img_pts = [np.array(i, dtype=float) for i in img_pts]
            img_pts = np.array(img_pts)
            ref_points = np.array(ref_points)
            
            # Calculate homography
            h, status = cv2.findHomography(img_pts, ref_points)
            h_inv = None
            if h is None:
                continue
            try:
                h_inv = np.linalg.inv(h)
            except:
                continue

            # Check if at least one other image point matches one other reference point
            for test_img_pt in all_img_pts:
                if not test_img_pt in img_pts:
                    for test_ref_pt in utils.reference_points:
                        if not list(test_ref_pt) in ref_points.tolist():
                            # Apply homography to reference test point
                            test_img_in_ref = cv2.perspectiveTransform(test_img_pt.reshape(1, 1, -1), h)[0][0]
                            # Check if it matches the image test point with an error of at most 2m
                            distance = np.linalg.norm(test_img_in_ref - test_ref_pt)
                            if distance < 2:
                                print(test_ref_pt)
                                print(ref_points)
                                print(test_img_pt)
                                print(img_pts)
                                print(test_img_in_ref)
                                print(distance)
                                print('-------------------------------------')
                                applyHomographyLine(img, h, h_inv)
                                return


def applyHomographyLine(img, h, h_inv):
    # Get offside player point (field image)
    print('Click on the offside player and then press [ENTER]')
    player_im = utils.get_points(img, 1)[0]
    #print(player_im)

    # Get corresponding offside player point in real world
    player_rw = cv2.perspectiveTransform(player_im.reshape(1, 1, -1), h)[0][0]
    #print(player_rw)

    # Get the two line points in the real world line (same x, y is the field bounds)
    line_point_1_rw = player_rw.copy()
    line_point_1_rw[1] = 0
    line_point_2_rw = player_rw.copy()
    line_point_2_rw[1] = 67
    #print(line_point_1_rw)
    #print(line_point_2_rw)

    # Get corresponding second point in the image
    line_point_1_im = cv2.perspectiveTransform(line_point_1_rw.reshape(1, 1, -1), h_inv)[0][0]
    line_point_2_im = cv2.perspectiveTransform(line_point_2_rw.reshape(1, 1, -1), h_inv)[0][0]
    #print(line_point_1_im)
    #print(line_point_2_im)

    # Draw line
    height, width, channels = img.shape
    blank_image = np.zeros((height,width,3), np.uint8)
    cv2.line(blank_image, tuple(line_point_1_im.astype(int)), tuple(line_point_2_im.astype(int)), (180,50,255), 5, cv2.LINE_AA)
    img = utils.blend_overlay_with_field(img,blank_image,0.5)

    cv2.imshow("Image", img)
    cv2.waitKey(0)


if __name__ == '__main__':
    debug = True

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
        if debug:
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
    if debug:
        for point in intersections:
            cv2.circle(img, point, 10, (0, 255, 0))

    # Homography
    if len(intersections) < 4:
        raise Exception('Not enough points were detected for a homography')

    findBestHomography()                  
