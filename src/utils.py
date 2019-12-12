import cv2
import numpy as np

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
