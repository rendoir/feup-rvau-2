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

    # Read source image.
    im_src = cv2.imread('../Homography/images/first-image.jpg')
    size = im_src.shape

    # Blank image.
    #im_src = np.zeros(shape=[500, 10, 3], dtype=np.uint8)
    #size = im_src.shape
    #cv2.imshow("Black Blank", im_src)
   
    # Create a vector of source points.
    pts_src = np.array(
                       [
                        [0,0],
                        [size[1] - 1, 0],
                        [size[1] - 1, size[0] -1],
                        [0, size[0] - 1 ]
                        ],dtype=float
                       )

    
    # Read destination image
    im_dst = cv2.imread('../img/football2.jpg')

    # Get four corners of the billboard
    print('Click on four corners of a billboard and then press ENTER')
    pts_dst = get_four_points(im_dst)
    
    # Calculate Homography between source and destination points
    h, status = cv2.findHomography(pts_src, pts_dst)
    
    # Warp source image
    im_temp = cv2.warpPerspective(im_src, h, (im_dst.shape[1],im_dst.shape[0]))

    # Black out polygonal area in destination image.
    cv2.fillConvexPoly(im_dst, pts_dst.astype(int), 0, 16)
    
    # Add warped source image to destination image.
    im_dst = im_dst + im_temp
    
    # Display image.
    cv2.imshow("Image", im_dst)
    cv2.waitKey(0)



