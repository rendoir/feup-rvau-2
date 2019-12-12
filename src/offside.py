#!/usr/bin/env python3

import cv2
import numpy as np
import sys
import utils

def blend_overlay_with_field(src_img,overlay,transparency):
    hsv = cv2.cvtColor(src_img, code=cv2.COLOR_BGR2HSV)
    # green range
    lower_green = np.array([30, 65, 65])
    upper_green = np.array([65, 255, 255])
    # layer masks
    field_mask = cv2.inRange(hsv, lower_green, upper_green)
    player_mask = cv2.bitwise_not(field_mask)
    # player_mask = cv2.morphologyEx(player_mask, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5)))
    # extract layers from original image
    field_layer = cv2.bitwise_and(src_img, src_img, mask=field_mask)
    player_layer = cv2.bitwise_and(src_img, src_img, mask=player_mask)
    # creates line that is blank where the players are
    overlay_layer = cv2.bitwise_and(field_layer,overlay)
    overlay_layer = cv2.GaussianBlur(overlay_layer,(3,3),cv2.BORDER_DEFAULT)
    field_layer = cv2.addWeighted(field_layer,1,overlay_layer,transparency,0)
    final = field_layer + player_layer
    return final


if __name__ == '__main__' :


    # Read destination image
    # 2008 UEFA Cup Final (Zenit Saint Petersburg vs Rangers) - Manchester City Stadium
    # Origin: Top Right. Field Size: 105m by 68m
    im_dst = cv2.imread('../img/football1.jpg')
    clean_img = cv2.imread('../img/football1.jpg')
   
    # Create a vector of source points.
    # Real-life Manchester City Stadium - Right Penalty Area Points
    pts_src = np.array(
        [
            [87.5, 12.84],      # Top Left
            [104,  12.84],      # Top Right
            [104,  53.16],      # Bottom Right
            [87.5, 53.16 ]      # Bottom Left
        ],dtype=float
    )

    # Get four corners of the penalty area
    print('Click on the four corners of the penalty area and then press [ENTER]')
    pts_dst = utils.get_points(im_dst, 4)
    #print(pts_dst)
    
    # Calculate Homography between source and destination points
    h, status = cv2.findHomography(pts_src, pts_dst)
    h_inv = np.linalg.inv(h)
    #print(h)

    # Get offside player point (field image)
    print('Click on the offside player and then press [ENTER]')
    player_im = utils.get_points(im_dst, 1)[0]
    #print(player_im)

    # Get corresponding offside player point in real world
    player_rw = cv2.perspectiveTransform(player_im.reshape(1, 1, -1), h_inv)[0][0]
    #print(player_rw)

    # Get the two line points in the real world line (same x, y is the field bounds)
    line_point_1_rw = player_rw.copy()
    line_point_1_rw[1] = 0
    line_point_2_rw = player_rw.copy()
    line_point_2_rw[1] = 67
    #print(line_point_1_rw)
    #print(line_point_2_rw)

    # Get corresponding second point in the image
    line_point_1_im = cv2.perspectiveTransform(line_point_1_rw.reshape(1, 1, -1), h)[0][0]
    line_point_2_im = cv2.perspectiveTransform(line_point_2_rw.reshape(1, 1, -1), h)[0][0]
    #print(line_point_1_im)
    #print(line_point_2_im)

    # Draw line
    height, width, channels = clean_img.shape
    blank_image = np.zeros((height,width,3), np.uint8)
    overlay_img = blank_image
    cv2.line(overlay_img, tuple(line_point_1_im.astype(int)), tuple(line_point_2_im.astype(int)), (0,0,255), 5, cv2.LINE_AA)

    final = blend_overlay_with_field(clean_img,overlay_img,1.0)

    # Display image.
    cv2.imshow("Image", final)
    cv2.waitKey(0)
