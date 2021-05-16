import math
from time import sleep


class Point:
    def __init__(self,  x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f'Point({self.x},{self.y})'


servo1_pos = Point(390, 50)
servo2_pos = Point(610, 50)
length_arm_b = 400
length_arm_a = 300
NEUNZIG_GRAD = math.pi / 2

CIRCLE_STEP = 1
real_width = 126.5
spacing = 36
real_height = 300.0

def frange(start, end, increment):
    f = start
    while f < end:
        yield f
        f += increment

class Sanduhr:
    def __init__(self, pca, id_left, id_right, id_stift):
        self.pca = pca
        self.id_left = id_left
        self.id_right = id_right
        self.id_stift = id_stift

    def stift_hoch(self):
        pass

    def stift_runter(self):
        pass

    def move_arms(self, left_angle, right_angle):
        # wir haben als Radius Teile von PI, der Servo braucht Grad-Zahlen
        left_angle = 225 - int(left_angle * 180.0 / math.pi)
        right_angle = 180 - int(right_angle * 180.0 / math.pi)
        print('MoveArms('+str(left_angle)+', '+str(right_angle)+')')
        self.pca.set_angle(self.id_left, left_angle)
        self.pca.set_angle(self.id_right, right_angle)
        sleep(0.2)

    def end_from_angle(self, starting_point, angle, length):
        a = length * math.sin(angle)
        b = length * math.cos(angle)
        ende_x = starting_point.x + b
        ende_y = starting_point.y + a
        ende = Point(ende_x, ende_y)

        return ende

    def calculate_angle(self, start, ende, seite):
        if (seite == 2):
            DR = ende.y - start.y  # check
            BR = (start.x) - ende.x  # check
            BD = math.sqrt(BR * BR + DR * DR)  # check
            r1 = math.atan(DR / BR)  # check außer rechts von servo2_pos
            w1 = math.acos(
                (length_arm_a ** 2 + BD ** 2 - length_arm_b ** 2)
                / (2 * length_arm_a * BD)
            )  # Kosinussatz
            alpha = 2 * NEUNZIG_GRAD - (r1 + w1)
            if (BR < 0):
                alpha = alpha - 2 * NEUNZIG_GRAD

        else:
            DR = ende.y - start.y
            AR = ende.x - start.x
            AD = math.sqrt(AR * AR + DR * DR)
            r1 = (math.asin(DR / AD))
            w1 = math.acos(
                (length_arm_a ** 2 + AD ** 2 - length_arm_b ** 2)
                / (2 * length_arm_a * AD)
            )  # Kosinussatz
            alpha = (r1 + w1)
            if (AR < 0):
                alpha = (NEUNZIG_GRAD * 2 - r1) + w1

        return alpha

    def move_arms_to(self, ende):
        alpha = self.calculate_angle(servo1_pos, ende, 1)
        beta = self.calculate_angle(servo2_pos, ende, 2)

        self.move_arms(alpha, beta)

    def draw_circle(self, radius_x, radius_y, mittelpunkt, start_winkel, end_winkel):
        self.stift_hoch()
        for winkel in frange(start_winkel, end_winkel, NEUNZIG_GRAD / 20):
            ende = self.end_from_angle(mittelpunkt, winkel, radius_x)
            #  skalieren, damit es ein Oval wird
            ende.y = mittelpunkt.y + \
                (ende.y - mittelpunkt.y) * (radius_y / radius_x)

            alpha = self.calculate_angle(servo1_pos, ende, 1)
            beta = self.calculate_angle(servo2_pos, ende, 2)
            self.stift_runter()
            self.move_arms(alpha, beta)

        ende = self.end_from_angle(mittelpunkt, winkel, radius_x)
        #  skalieren, damit es ein Oval wird
        ende.y = mittelpunkt.y + \
            (ende.y - mittelpunkt.y) * (radius_y / radius_x)

        alpha = self.calculate_angle(servo1_pos, ende, 1)
        beta = self.calculate_angle(servo2_pos, ende, 2)

        self.move_arms(alpha, beta)

    def draw_line(self, start, end):
        if (end.y >= start.y):
            a = start.y - end.y
        else:
            a = end.y - start.y

        if (start.x >= end.x):
            b = end.x - start.x
        else:
            b = end.x - start.x

        c = math.sqrt((a ** 2) + (b ** 2))

        abstand = c / 25
        angle = math.acos(b / c)

        if (start.y > end.y):
            angle = 2 * math.pi - angle

        self.move_arms_to(start)
        for actual_abstand in frange(abstand, c, abstand):

            ende = self.end_from_angle(start, angle, actual_abstand)
            self.move_arms_to(ende)

        self.move_arms_to(end)

    def draw_number_one(self, start, höhe, breite):

        current_position = Point(start.x, start.y - (2 / 3 * höhe))

        self.move_arms_to(current_position)

        self.stift_runter()

        future_position = Point(start.x + breite,  start.y - höhe)

        self.draw_line(current_position, future_position)
        current_position = future_position
        future_position = Point(start.x + breite, start.y)
        self.draw_line(current_position, future_position)

        self.stift_hoch()

    def draw_number_two(self, start, höhe, breite):

        viertel_zwei = höhe / 4

        current_position = Point(start.x + breite / 2,
                                 start.y - (höhe - viertel_zwei))

        self.stift_runter()

        future_position = Point(
            start.x + breite, start.y - (höhe - viertel_zwei))
        self.draw_circle(breite / 2, viertel_zwei, current_position,
                         2 * NEUNZIG_GRAD, 4 * NEUNZIG_GRAD)
        self.draw_line(future_position, start)
        current_position = start
        future_position = Point(start.x + breite, start.y)
        self.draw_line(current_position, future_position)
        self.stift_hoch()

    def draw_number_three(self, start, höhe, breite):

        viertel_drei = höhe / 4

        current_position = Point(start.x + breite / 2,
                                 start.y - höhe + viertel_drei)

        self.stift_runter()

        future_position = Point(start.x + breite / 2, start.y - viertel_drei)
        self.draw_circle(breite / 2, viertel_drei, current_position,
                         2 * NEUNZIG_GRAD, 5 * NEUNZIG_GRAD)
        self.draw_circle(breite / 2, viertel_drei, future_position,
                         3 * NEUNZIG_GRAD, 6 * NEUNZIG_GRAD)
        self.stift_hoch()

    def draw_number_four(self, start, höhe, breite):

        current_position = Point(start.x + breite, start.y - höhe * 0.4)

        self.move_arms_to(current_position)

        self.stift_runter()
        future_position = Point(start.x,  start.y - höhe * 0.4)
        self.draw_line(current_position, future_position)

        current_position = future_position
        future_position = Point(start.x + breite / 2,  start.y - höhe)
        self.draw_line(current_position, future_position)
        self.stift_hoch()

        future_position = Point(start.x + breite / 2,  start.y - höhe * 0.6)
        self.move_arms_to(future_position)

        current_position = future_position
        future_position = Point(start.x + breite / 2,  start.y)
        self.stift_runter()
        self.draw_line(current_position, future_position)
        self.stift_hoch()

    def draw_number_five(self, start, höhe, breite):

        viertel_vier = höhe / 4

        current_position = Point(start.x + breite,  start.y - höhe)

        self.move_arms_to(current_position)

        self.stift_runter()
        future_position = Point(start.x,  start.y - höhe)
        self.draw_line(current_position, future_position)
        current_position = future_position
        future_position = Point(start.x,  start.y - 2 * viertel_vier)
        self.draw_line(current_position, future_position)
        current_position = future_position
        future_position = Point(start.x + breite / 2,
                                start.y - 2 * viertel_vier)
        self.draw_line(current_position, future_position)
        future_position = Point(start.x + breite / 2,  start.y - höhe / 4)
        self.draw_circle(breite / 2, viertel_vier, future_position,
                         3 * NEUNZIG_GRAD, 6 * NEUNZIG_GRAD)
        self.stift_hoch()

    def draw_number_six(self, start, höhe, breite):

        viertel_sechs = höhe / 4

        future_position = Point(start.x + breite / 2,  start.y - viertel_sechs)

        self.stift_runter()
        self.draw_circle(breite / 2, viertel_sechs,
                         future_position, 0, 4 * NEUNZIG_GRAD)
        current_position = Point(start.x,  start.y - breite / 2)
        future_position = Point(start.x,  start.y - (höhe - breite / 2))
        self.draw_line(current_position, future_position)
        current_position = Point(start.x + breite / 2,
                                 start.y - (höhe - viertel_sechs))
        self.draw_circle(breite / 2, viertel_sechs, current_position,
                         2 * NEUNZIG_GRAD, 4 * NEUNZIG_GRAD)
        self.stift_hoch()

    def draw_number_seven(self, start, höhe, breite):

        current_position = Point(start.x,  start.y - höhe)

        self.move_arms_to(current_position)

        self.stift_runter()

        future_position = Point(start.x + breite,  start.y - höhe)
        self.draw_line(current_position, future_position)

        current_position = future_position
        future_position = start
        self.draw_line(current_position, future_position)

        current_position = Point(start.x,  start.y - höhe / 2)
        future_position = Point(start.x + breite,  start.y - höhe / 2)
        self.draw_line(current_position, future_position)
        self.stift_hoch()

    def draw_number_eight(self, start, höhe, breite):

        viertel_acht = höhe / 4

        current_position = Point(start.x + breite / 2,  start.y - viertel_acht)
        self.stift_runter()
        self.draw_circle(breite / 2, viertel_acht,
                         current_position, 0, 4 * NEUNZIG_GRAD)
        self.stift_hoch()
        current_position.y -= 2 * viertel_acht
        self.stift_runter()
        self.draw_circle(breite / 2, viertel_acht,
                         current_position, 0, 4 * NEUNZIG_GRAD)
        self.stift_hoch()

    def draw_number_nine(self, start, höhe, breite):

        viertel_neun = höhe / 4

        self.stift_runter()

        future_position = Point(start.x + breite / 2,
                                start.y - (höhe - viertel_neun))

        self.draw_circle(breite / 2, viertel_neun,
                         future_position, 0, 4 * NEUNZIG_GRAD)

        current_position = Point(start.x + breite,  start.y - breite / 2)
        future_position = Point(
            start.x + breite,  start.y - (höhe - viertel_neun))
        self.draw_line(future_position, current_position)
        current_position = Point(start.x + breite / 2,  start.y - viertel_neun)
        self.draw_circle(breite / 2, viertel_neun,
                         current_position, 0, 2 * NEUNZIG_GRAD)
        self.stift_hoch()

    def draw_number_zero(self, start, höhe, breite):

        viertel_null = höhe / 4

        current_position = Point(start.x + breite / 2,
                                 start.y - 3 * viertel_null)

        self.draw_circle(breite / 2, viertel_null, current_position,
                         2 * NEUNZIG_GRAD, 4 * NEUNZIG_GRAD)

        current_position = Point(start.x + breite,  start.y - 3 * viertel_null)
        future_position = Point(start.x + breite,  start.y - viertel_null)

        self.draw_line(current_position, future_position)
        current_position = Point(start.x + breite / 2,  start.y - viertel_null)
        self.draw_circle(breite / 2, viertel_null,
                         current_position, 0, 2 * NEUNZIG_GRAD)
        current_position = Point(start.x,  start.y - viertel_null)
        future_position = Point(start.x,  start.y - 3 * viertel_null)
        self.draw_line(current_position, future_position)

    def draw_number(self, position, number):

        actual_start = Point(150 + (position - 1) *
                             (real_width + spacing),  550)

        if (position > 2):
            actual_start.x += spacing

        number_painter = [self.draw_number_zero, self.draw_number_one, self.draw_number_two, self.draw_number_three, self.draw_number_four,
                          self.draw_number_five, self.draw_number_six, self.draw_number_seven, self.draw_number_eight, self.draw_number_nine]
        number_painter[number](actual_start, real_height, real_width)

    def draw_doppelpunkt(self, start):
        punkt_unten = Point(start.x + real_width / 2,
                            start.y + (1 / 3) * real_height)
        punkt_oben = Point(start.x + real_width / 2,
                           start.y + (2 / 3) * real_height)
        self.stift_hoch()
        self.move_arms_to(punkt_unten)
        self.stift_runter()
        self.stift_hoch()
        self.move_arms_to(punkt_oben)
        self.stift_runter()
        self.stift_hoch()

    def draw_time(self, first_digit, second_digit, third_digit, fourth_digit):
        self.draw_number(1, first_digit)
        self.draw_number(2, second_digit)
        self.draw_doppelpunkt(Point(150,  250), Point(300, 650))
        self.draw_number(3, third_digit)
        self.draw_number(4, fourth_digit)
