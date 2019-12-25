import cv2
import math
import utils
import numpy as np
from itertools import permutations



def findBestHomography():
    # Loop through all the possible permutations of 4 points in the image
    all_img_pts = [np.array(i, dtype=float) for i in intersections]
    for img_pts in permutations(intersections, 4):
        # Optimization: check if polygon is convex and clockwise
        if not utils.isConvex(img_pts) or not utils.isClockwise(img_pts):
            continue

        # Loop through all the possible permutations of 4 points in the reference
        for ref_points in permutations(utils.reference_points_right, 4):
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
                    for test_ref_pt in utils.reference_points_right:
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
                                applyHomographyLine(img, img_pts, ref_points)
                                return


def applyHomographyLine(img, img_pts, ref_points):
    ref_points *= quality
    utils.middle_goal_line_right *= quality

    # Calculate Homography between source and destination points
    h, status = cv2.findHomography(ref_points, img_pts)
    h_inv = np.linalg.inv(h)
    #print(h)

    # Get ball point (field image)
    print('Click on the ball and then press [ENTER]')
    ball_im = utils.get_points(img, 1)[0]
    #print(ball_im)

    # Get corresponding ball point in real world
    ball_rw = cv2.perspectiveTransform(ball_im.reshape(1, 1, -1), h_inv)[0][0]
    #print(ball_rw)
    
    # Draw circle
    overlay_rw = np.zeros((68*quality, 105*quality, 3), np.uint8)
    if draw_circle:
        cv2.circle(overlay_rw, tuple(ball_rw.astype(int)), int(9.15*quality), (0,0,255), 1*quality, lineType=cv2.LINE_AA)
        #cv2.imshow("Overlay Real-world", overlay_rw)
    
    # Draw line
    if draw_line:
        cv2.line(overlay_rw, tuple(ball_rw.astype(int)), tuple(utils.middle_goal_line_right.astype(int)), (128,128,128), 1*quality, cv2.LINE_AA)

    # Warp overlay
    overlay_img = cv2.warpPerspective(overlay_rw, h, (img.shape[1],img.shape[0]), cv2.INTER_LANCZOS4)
    #cv2.imshow("Overlay Warped", overlay_img)

    # Draw text
    height, width, channels = img.shape
    overlay_text = np.zeros((height,width,3), np.uint8)
    if draw_text:
        distance = np.linalg.norm(ball_rw - utils.middle_goal_line_right) / quality
        text_location = (int(overlay_text.shape[1] * 0.1), int(overlay_text.shape[0] * 0.8))
        cv2.putText(overlay_text, "%.2f" % distance + 'm', text_location, cv2.FONT_HERSHEY_DUPLEX, 1, (255,255,255), 2, cv2.LINE_AA)
    
    # Merge overlay
    final = utils.blend_overlay_with_field(img,overlay_img,0.5)
    cv2.add(overlay_text, final, final)

    # Display image.
    cv2.imshow("Image", final)
    cv2.waitKey(0)


if __name__ == '__main__':
    quality = 100
    draw_circle = True
    draw_line = True
    draw_text = True
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
            lns.append(utils.Line(pt1, pt2))

    # Calculate intersection points
    intersections = []
    for i in range(0, len(lns)):
        for j in range(i + 1, len(lns)):
            point = lns[i].intersection(lns[j])
            if not point is None:
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
