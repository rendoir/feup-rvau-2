#!/usr/bin/env python3

import cv2
import numpy as np
import sys

def mouse_handler(event, x, y, flags, data) :

    if event == cv2.EVENT_LBUTTONDOWN :
        if len(data['points']) < data['max_points'] :
            cv2.circle(data['im'], (x,y), 3, (0,0,255), 5, 16)
            cv2.imshow("Image", data['im'])
            data['points'].append([x,y])

def get_points(im, max_points) :

    # Set up data to send to mouse handler
    data = {}
    data['im'] = im.copy()
    data['points'] = []
    data['max_points'] = max_points
    
    #Set the callback function for any mouse event
    cv2.imshow("Image",im)
    cv2.setMouseCallback("Image", mouse_handler, data)
    cv2.waitKey(0)
    cv2.setMouseCallback("Image", lambda *args : None)
    
    # Convert array to np.array
    points = np.vstack(data['points']).astype(float)
    
    return points


if __name__ == '__main__' :


    # Read destination image
    # 2008 UEFA Cup Final (Zenit Saint Petersburg vs Rangers) - Manchester City Stadium
    # Origin: Top Right. Field Size: 105m by 68m
    im_dst = cv2.imread('../img/football2.jpg')
   
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
    pts_dst = get_points(im_dst, 4)
    
    # Calculate Homography between source and destination points
    h, status = cv2.findHomography(pts_src, pts_dst)
    h_inv = np.linalg.inv(h)
    print(h)

    # Get offside player point
    print('Click on the offside player and then press [ENTER]')
    player_pts = get_points(im_dst, 1)

    # Line Points in the Real World 
    line_src = np.float32([87.5, 12.84, 90, 12.84, 90, 53.16, 87.5, 53.16]).reshape(4, 1, -1)
    
    # Apply perspective tranform to the line points
    line_dst = cv2.perspectiveTransform(line_src, h)
    print(line_dst)

    # Black out polygonal area in destination image.
    cv2.fillConvexPoly(im_dst, line_dst.astype(int), 0, 16)

    # Display image.
    cv2.imshow("Image", im_dst)
    cv2.waitKey(0)



