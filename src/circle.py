#!/usr/bin/env python3

import cv2
import numpy as np
import sys
import utils


if __name__ == '__main__' :


    # Read destination image
    # 2018 World Cup (Colombia vs Japan) - Mordovia Arena
    # Origin: Top Right. Field Size: 105m by 68m
    im_dst = cv2.imread('../img/football2.png')
   
    # Create a vector of source points.
    # Real-life Mordovia Arena - Left Goal Area Points
    pts_src = np.array(
        [
            [0,   24.84],      # Top Left
            [5.5, 24.84],      # Top Right
            [5.5, 43.16],      # Bottom Right
            [0,   43.16 ]      # Bottom Left
        ],dtype=float
    )

    # Get four corners of the goal area
    print('Click on the four corners of the goal area and then press [ENTER]')
    pts_dst = utils.get_points(im_dst, 4)
    #print(pts_dst)
    
    # Calculate Homography between source and destination points
    h, status = cv2.findHomography(pts_src, pts_dst)
    h_inv = np.linalg.inv(h)
    #print(h)

    # Get ball point (field image)
    print('Click on the offside player and then press [ENTER]')
    ball_im = utils.get_points(im_dst, 1)[0]
    #print(ball_im)

    # Get corresponding ball point in real world
    ball_rw = cv2.perspectiveTransform(ball_im.reshape(1, 1, -1), h_inv)[0][0]
    #print(ball_rw)
    
    # Draw circle
    overlay_rw = np.zeros((68, 105, 3), np.uint8)
    cv2.circle(overlay_rw, tuple(ball_rw.astype(int)), int(9.15), (0,0,255), cv2.FILLED)
    cv2.imshow("Overlay Real-world", overlay_rw)
    overlay_img = cv2.warpPerspective(overlay_rw, h, (im_dst.shape[1],im_dst.shape[0]))
    cv2.imshow("Overlay Warped", overlay_img)
    #cv2.add(overlay_img, im_dst, im_dst)

    # Display image.
    cv2.imshow("Image", im_dst)
    cv2.waitKey(0)
