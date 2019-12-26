import cv2
import numpy as np
import math


class Line:
    def __init__(self, pt1, pt2):
        self.pt1 = pt1
        self.pt2 = pt2
        self.dx = pt2[0] - pt1[0]
        self.dy = pt2[1] - pt1[1]
        if self.dx == 0:
            self.m = math.inf
        else:
            self.m = self.dy / self.dx
        self.b = pt1[1] - self.m * pt1[0]

    def intersection(self, other):
        if math.isinf(self.m) or math.isinf(other.m) or (self.m - other.m) == 0:
            return None
        x = (other.b - self.b) / (self.m - other.m)
        y = self.m * x + self.b
        return (int(x), int(y))


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
    lower_green = np.array([35, 60, 60])
    upper_green = np.array([65, 255, 255])
    # layer masks
    field_mask = cv2.inRange(hsv, lower_green, upper_green)
    player_mask = cv2.bitwise_not(field_mask)
    # player_mask = cv2.morphologyEx(player_mask, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5)))
    # extract layers from original image
    field_layer = cv2.bitwise_and(src_img, src_img, mask=field_mask)
    player_layer = cv2.bitwise_and(src_img, src_img, mask=player_mask)
    # creates line that is blank where the players are
    overlay_layer = cv2.bitwise_and(overlay,overlay,mask=field_mask)
    #overlay_layer = cv2.GaussianBlur(overlay_layer,(3,3),cv2.BORDER_DEFAULT)
    field_layer = cv2.addWeighted(field_layer,1,overlay_layer,transparency,0)
    final = field_layer + player_layer
    return final

def GetFieldLayer(src_img):
    hsv = cv2.cvtColor(src_img, code=cv2.COLOR_BGR2HSV)
    # green range
    lower_green = np.array([35, 10, 60])
    upper_green = np.array([65, 255, 255])
    # layer masks
    field_mask = cv2.inRange(hsv, lower_green, upper_green)
    player_mask = cv2.bitwise_not(field_mask)
    # player_mask = cv2.morphologyEx(player_mask, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5)))
    # extract layers from original image
    field_layer = cv2.bitwise_and(src_img, src_img, mask=field_mask)
    return field_layer


TWO_PI = 2 * math.pi
# Credits to Rory Daulton
def isConvex(polygon):
    """Return True if the polynomial defined by the sequence of 2D
    points is 'strictly convex': points are valid, side lengths non-
    zero, interior angles are strictly between zero and a straight
    angle, and the polygon does not intersect itself.

    NOTES:  1.  Algorithm: the signed changes of the direction angles
                from one side to the next side must be all positive or
                all negative, and their sum must equal plus-or-minus
                one full turn (2 pi radians). Also check for too few,
                invalid, or repeated points.
            2.  No check is explicitly done for zero internal angles
                (180 degree direction-change angle) as this is covered
                in other ways, including the `n < 3` check.
    """
    try:  # needed for any bad points or direction changes
        # Check for too few points
        if len(polygon) < 3:
            return False
        # Get starting information
        old_x, old_y = polygon[-2]
        new_x, new_y = polygon[-1]
        new_direction = math.atan2(new_y - old_y, new_x - old_x)
        angle_sum = 0.0
        # Check each point (the side ending there, its angle) and accum. angles
        for ndx, newpoint in enumerate(polygon):
            # Update point coordinates and side directions, check side length
            old_x, old_y, old_direction = new_x, new_y, new_direction
            new_x, new_y = newpoint
            new_direction = math.atan2(new_y - old_y, new_x - old_x)
            if old_x == new_x and old_y == new_y:
                return False  # repeated consecutive points
            # Calculate & check the normalized direction-change angle
            angle = new_direction - old_direction
            if angle <= -math.pi:
                angle += TWO_PI  # make it in half-open interval (-Pi, Pi]
            elif angle > math.pi:
                angle -= TWO_PI
            if ndx == 0:  # if first time through loop, initialize orientation
                if angle == 0.0:
                    return False
                orientation = 1.0 if angle > 0.0 else -1.0
            else:  # if other time through loop, check orientation is stable
                if orientation * angle <= 0.0:  # not both pos. or both neg.
                    return False
            # Accumulate the direction-change angle
            angle_sum += angle
        # Check that the total number of full turns is plus-or-minus 1
        return abs(round(angle_sum / TWO_PI)) == 1
    except (ArithmeticError, TypeError, ValueError):
        return False  # any exception means not a proper convex polygon

def signedArea(pts):
    xs,ys = map(list, zip(*pts))
    xs.append(xs[0])
    ys.append(ys[0])
    area = 0
    for i in range(len(xs) - 1):
        edge = (xs[i+1] - xs[i]) * (ys[i+1] + ys[i])
        area += edge
    return area

def isClockwise(pts):
    return signedArea(pts) > 0


# 105x68 Field, origin on the left upper corner, clock-wise order
reference_points_right = np.array([
    # Right penalty area
    [88.5, 13.84], [105, 13.84],
    [105, 54.16], [88.5, 54.16],

    # Right upper corner 
    [105, 0]
], dtype=float)

middle_goal_line_right = np.array([105, 34], dtype=float)
