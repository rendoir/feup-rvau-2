import cv2
import numpy as np
import sys

if __name__ == '__main__':
    img = cv2.imread("../../img/football1.jpg", 1)
    cv2.imshow("Original", img)

    # convert the image to hsv for the layer masks
    hsv = cv2.cvtColor(img, code=cv2.COLOR_BGR2HSV)

    # green range
    lower_green = np.array([30, 65, 65])
    upper_green = np.array([65, 255, 255])

    # layer masks
    field_mask = cv2.inRange(hsv, lower_green, upper_green)
    player_mask = cv2.bitwise_not(field_mask)

    # extract layers from original image
    field_layer = cv2.bitwise_and(img, img, mask=field_mask)
    player_layer = cv2.bitwise_and(img, img, mask=player_mask)

    cv2.imshow("Soccer Field Layer", field_layer)
    cv2.imshow("Players Layer", player_layer)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
