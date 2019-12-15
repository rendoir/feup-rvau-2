#!/usr/bin/env python3

import cv2
import numpy as np
import sys
import utils


if __name__ == '__main__' :

    quality = 100

    # Read destination image
    # 2018 World Cup (Colombia vs Japan) - Mordovia Arena
    # Origin: Top Right. Field Size: 105m by 68m
    im_dst = cv2.imread('../img/football2.png')
   
    # Create a vector of source points.
    # Real-life Mordovia Arena - Left Goal Area Points
    middle_of_goal_line = np.array([0, 34], dtype=float)
    pts_src = np.array(
        [
            [0,   24.84],      # Top Left
            [5.5, 24.84],      # Top Right
            [5.5, 43.16],      # Bottom Right
            [0,   43.16 ]      # Bottom Left
        ],dtype=float
    )
    pts_src *= quality
    middle_of_goal_line *= quality

    # Get four corners of the goal area
    print('Click on the four corners of the goal area and then press [ENTER]')
    pts_dst = utils.get_points(im_dst, 4)
    #print(pts_dst)
    
    # Calculate Homography between source and destination points
    h, status = cv2.findHomography(pts_src, pts_dst)
    h_inv = np.linalg.inv(h)
    #print(h)

    # Get ball point (field image)
    print('Click on the ball and then press [ENTER]')
    ball_im = utils.get_points(im_dst, 1)[0]
    #print(ball_im)

    # Get corresponding ball point in real world
    ball_rw = cv2.perspectiveTransform(ball_im.reshape(1, 1, -1), h_inv)[0][0]
    #print(ball_rw)
    
    # Draw circle
    overlay_rw = np.zeros((68*quality, 105*quality, 3), np.uint8)
    cv2.circle(overlay_rw, tuple(ball_rw.astype(int)), int(9.15*quality), (0,0,255), 1*quality, lineType=cv2.LINE_AA)
    #cv2.imshow("Overlay Real-world", overlay_rw)
    
    # Draw line
    cv2.line(overlay_rw, tuple(ball_rw.astype(int)), tuple(middle_of_goal_line.astype(int)), (64,64,64), 1*quality, cv2.LINE_AA)

    # Warp overlay
    overlay_img = cv2.warpPerspective(overlay_rw, h, (im_dst.shape[1],im_dst.shape[0]), cv2.INTER_LANCZOS4)
    #cv2.imshow("Overlay Warped", overlay_img)

    # Draw text
    height, width, channels = im_dst.shape
    overlay_text = np.zeros((height,width,3), np.uint8)
    distance = np.linalg.norm(ball_rw - middle_of_goal_line) / quality
    text_location = (int(overlay_text.shape[1] * 0.1), int(overlay_text.shape[0] * 0.8))
    cv2.putText(overlay_text, "%.2f" % distance + 'm', text_location, cv2.FONT_HERSHEY_DUPLEX, 1, (255,255,255), 2, cv2.LINE_AA)
    
    # Merge overlay
    final = utils.blend_overlay_with_field(im_dst,overlay_img,0.5)
    cv2.add(overlay_text, final, final)

    # Display image.
    cv2.imshow("Image", final)
    cv2.waitKey(0)
