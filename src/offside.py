#!/usr/bin/env python3

import cv2
import numpy as np
import sys

def mouse_handler(event, x, y, flags, data) :

    if event == cv2.EVENT_LBUTTONDOWN :
        if len(data['points']) < 4 :
            cv2.circle(data['im'], (x,y), 3, (0,0,255), 5, 16)
            cv2.imshow("Image", data['im'])
            data['points'].append([x,y])

def get_four_points(im) :

    # Set up data to send to mouse handler
    data = {}
    data['im'] = im.copy()
    data['points'] = []
    
    #Set the callback function for any mouse event
    cv2.imshow("Image",im)
    cv2.setMouseCallback("Image", mouse_handler, data)
    cv2.waitKey(0)
    
    # Convert array to np.array
    points = np.vstack(data['points']).astype(float)
    
    return points


if __name__ == '__main__' :


    # Read destination image
    # 2008 UEFA Cup Final (Zenit Saint Petersburg vs Rangers) - Manchester City Stadium
    # Origin: Top Right. Field Size: 105m by 68m
    im_dst = cv2.imread('../img/football2.jpg')

    # Blank image.
    im_src = np.zeros(shape=[68, 105, 3], dtype=np.uint8)
    im_src[:] = (0, 0, 255)
    size = im_src.shape
    cv2.imshow("Real Life", im_src)
   
    # Create a vector of source points.
    # Real-life Manchester City Stadium - Right Penalty Area Points
    pts_src = np.array(
        [
            [16.5, 13.84],      # Top Left
            [0,    13.84],      # Top Right
            [0,    54.16],      # Bottom Right
            [16.5, 54.16 ]      # Bottom Left
        ],dtype=float
    )

    # Get four corners of the billboard
    print('Click on four corners of a billboard and then press ENTER')
    pts_dst = get_four_points(im_dst)
    
    # Calculate Homography between source and destination points
    h, status = cv2.findHomography(pts_src, pts_dst)
    
    # Warp source image
    im_temp = cv2.warpPerspective(im_src, h, (im_dst.shape[1],im_dst.shape[0]))

    # Black out polygonal area in destination image.
    cv2.fillConvexPoly(im_dst, pts_dst.astype(int), 0, 1)
    
    # Add warped source image to destination image.
    im_dst = im_dst + im_temp

    cv2.imshow("Warped Image", im_temp)
    
    # Display image.
    cv2.imshow("Image", im_dst)
    cv2.waitKey(0)



