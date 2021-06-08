import math
from time import sleep
from machine import Pin, I2C
from pca9685 import PCA9685

# for-Loop-Erweiterung für beliebige inkrementierbare Datentypen, range() geht nur für integer

def frange(start, end, increment):
    f = start
    while f < end:
        yield f
        f += increment

# Speicher für X/Y-Koordinaten
class Point:
    def __init__(self,  x, y):
        self.x = x
        self.y = y

# Positionen der Servo-Drehpunkte und des Sandkastens im Koordinatensystem
servo1_pos = Point(390, 50)
servo2_pos = Point(610, 50)
sandbox_start = Point(170, 580)

# Länge der Arme im Koordinatensystem
length_arm_b = 400
length_arm_a = 320

NEUNZIG_GRAD = math.pi / 2

CIRCLE_STEP = 1
# Breite einer Ziffer
real_width = 110
# Höhe einer Ziffer
real_height = 230.0
half_height = real_height / 2
quarter_height = real_height / 4

# Abstand zwischen zwei Ziffern
spacing = 36


class Sanduhr:
    def __init__(self):
        self.id_left = 14
        self.id_right = 15
        self.id_stift = 12
        self.init_hardware()

        self.stift_ist_hoch = False
        self.stift_hoch()
        self.move_arms(3 * NEUNZIG_GRAD / 2, NEUNZIG_GRAD / 2)

    def init_hardware(self):
        # init Servo-Treiber
        self.pca = PCA9685()
        self.pca.frequeny = 50
        self.pca.init_servo(self.id_left, 320, 2140, 177)
        self.pca.init_servo(self.id_right, 320, 2140, 177)
        self.pca.init_servo(self.id_stift, 320, 2140, 177)

    def stift_hoch(self):
        if not self.stift_ist_hoch:
            for i in range(47, 30, -1):
                self.pca.set_angle(self.id_stift, i)
                sleep(0.01)
        self.stift_ist_hoch = True
        sleep(0.5)

    def stift_runter(self):
        if self.stift_ist_hoch:
            for i in range(30, 47, 1):
                self.pca.set_angle(self.id_stift, i)
                sleep(0.01)
        self.stift_ist_hoch = False

    def move_arms(self, left_angle, right_angle):
        # wir haben als Radius Teile von PI, der Servo braucht Grad-Zahlen
        # außerdem läuft der Servo in die umgekehrte Richtung der Simulatiom
        left_angle = 222 - (left_angle * 180.0 / math.pi)
        right_angle = 142 - (right_angle * 180.0 / math.pi)
        self.pca.set_angle(self.id_left, left_angle)
        self.pca.set_angle(self.id_right, right_angle)
        sleep(0.05)

    def end_from_angle(self, starting_point, angle, length):
        a = length * math.sin(angle)
        b = length * math.cos(angle)
        return Point(starting_point.x + b, starting_point.y + a)

    def calculate_angle(self, start, ende, seite):
        if (seite == 2):
            DR = ende.y - start.y
            BR = start.x - ende.x
            BD = math.sqrt(BR * BR + DR * DR)
            r1 = math.atan(DR / BR)
            w1 = math.acos(
                (length_arm_a ** 2 + BD ** 2 - length_arm_b ** 2)
                / (2 * length_arm_a * BD)
            )  # Kosinussatz
            alpha = 2 * NEUNZIG_GRAD - (r1 + w1)
            if BR < 0:
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
            alpha = r1 + w1
            if AR < 0:
                alpha = (NEUNZIG_GRAD * 2 - r1) + w1

        return alpha

    def move_arms_to(self, ende):
        alpha = self.calculate_angle(servo1_pos, ende, 1)
        beta = self.calculate_angle(servo2_pos, ende, 2)
        self.move_arms(alpha, beta)

    def draw_circle(self, radius_x, radius_y, mittelpunkt, start_winkel, end_winkel):
        for winkel in frange(start_winkel, end_winkel, NEUNZIG_GRAD / 20):
            pos = self.end_from_angle(mittelpunkt, winkel, radius_x)
            #  skalieren, damit es ein Oval wird
            pos.y = mittelpunkt.y + \
                (pos.y - mittelpunkt.y) * (radius_y / radius_x)

            self.move_arms_to(pos)
            self.stift_runter()

        pos = self.end_from_angle(mittelpunkt, winkel, radius_x)
        #  skalieren, damit es ein Oval wird
        pos.y = mittelpunkt.y + (pos.y - mittelpunkt.y) * (radius_y / radius_x)

        self.move_arms_to(pos)

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

        abstand = real_height / 60
        angle = math.acos(b / c)

        if (start.y > end.y):
            angle = 2 * math.pi - angle

        self.move_arms_to(start)
        for actual_abstand in frange(abstand, c, abstand):
            ende = self.end_from_angle(start, angle, actual_abstand)
            self.move_arms_to(ende)

        self.move_arms_to(end)

    def draw_number_one(self, start, höhe, breite):

        pos = Point(start.x, start.y - (2 / 3 * höhe))
        self.move_arms_to(pos)
        self.stift_runter()
        next_pos = Point(start.x + breite,  start.y - höhe)
        self.draw_line(pos, next_pos)
        pos = next_pos
        next_pos = Point(start.x + breite, start.y)
        self.draw_line(pos, next_pos)
        self.stift_hoch()

    def draw_number_two(self, start, height, width):
        pos = Point(start.x + width / 2,
                    start.y - (height - quarter_height))
        # draw_circle macht den Stift runter
        self.draw_circle(width / 2, quarter_height, pos,
                         2 * NEUNZIG_GRAD, 4 * NEUNZIG_GRAD)
        pos = Point(start.x + width, start.y - (height - quarter_height))
        self.draw_line(pos, start)
        pos = Point(start.x + width, start.y)
        self.draw_line(start, pos)
        self.stift_hoch()

    def draw_number_three(self, start, height, width):
        pos = Point(start.x + width / 2,
                    start.y - height + quarter_height)
        # draw_circle macht den Stift runter
        self.draw_circle(width / 2, quarter_height, pos,
                         2 * NEUNZIG_GRAD, 5 * NEUNZIG_GRAD)

        pos = Point(start.x + width / 2, start.y - quarter_height)
        self.draw_circle(width / 2, quarter_height, pos,
                         3 * NEUNZIG_GRAD, 6 * NEUNZIG_GRAD)
        self.stift_hoch()

    def draw_number_four(self, start, height, width):

        pos = Point(start.x + width, start.y - height * 0.4)
        next_pos = Point(start.x,  start.y - height * 0.4)

        self.move_arms_to(pos)
        self.stift_runter()
        self.draw_line(pos, next_pos)

        pos = Point(start.x + width / 2,  start.y - height)
        self.draw_line(next_pos, pos)
        self.stift_hoch()

        pos = Point(start.x + width / 2,  start.y - height * 0.6)
        next_pos = Point(start.x + width / 2,  start.y)

        self.move_arms_to(pos)
        self.stift_runter()
        self.draw_line(pos, next_pos)
        self.stift_hoch()

    def draw_number_five(self, start, height, width):
        pos = Point(start.x + width,  start.y - height)
        self.move_arms_to(pos)

        self.stift_runter()
        next_pos = Point(start.x,  start.y - height)
        self.draw_line(pos, next_pos)
        pos = Point(start.x,  start.y - half_height)
        self.draw_line(next_pos, pos)
        next_pos = Point(start.x + width / 2,
                         start.y - half_height)
        self.draw_line(pos, next_pos)
        next_pos = Point(start.x + width / 2,  start.y - height / 4)
        self.draw_circle(width / 2, quarter_height, next_pos,
                         3 * NEUNZIG_GRAD, 6 * NEUNZIG_GRAD)
        self.stift_hoch()

    def draw_number_six(self, start, height, width):
        pos = Point(start.x + width / 2,  start.y - quarter_height)
        self.draw_circle(width / 2, quarter_height,
                         pos, 0, 4 * NEUNZIG_GRAD)

        next_pos = Point(start.x,  start.y - width / 2)
        pos = Point(start.x,  start.y - (height - width / 2))
        self.draw_line(next_pos, pos)

        pos = Point(start.x + width / 2,
                    start.y - (height - quarter_height))
        self.draw_circle(width / 2, quarter_height, pos,
                         2 * NEUNZIG_GRAD, 4 * NEUNZIG_GRAD)
        self.stift_hoch()

    def draw_number_seven(self, start, height, width):

        pos = Point(start.x,  start.y - height)
        self.move_arms_to(pos)

        next_pos = Point(start.x + width,  start.y - height)
        self.stift_runter()
        self.draw_line(pos, next_pos)
        self.draw_line(next_pos, start)

        pos = Point(start.x,  start.y - half_height)
        next_pos = Point(start.x + width,  start.y - half_height)
        self.draw_line(pos, next_pos)
        self.stift_hoch()

    def draw_number_eight(self, start, height, width):
        pos = Point(start.x + width / 2,  start.y - quarter_height)
        self.draw_circle(width / 2, quarter_height,
                         pos, 0, 4 * NEUNZIG_GRAD)
        self.stift_hoch()
        pos.y -= half_height
        self.stift_runter()
        self.draw_circle(width / 2, quarter_height,
                         pos, 0, 4 * NEUNZIG_GRAD)
        self.stift_hoch()

    def draw_number_nine(self, start, höhe, breite):

        pos = Point(start.x + breite / 2,
                    start.y - (höhe - quarter_height))

        self.draw_circle(breite / 2, quarter_height,
                         pos, 0, 4 * NEUNZIG_GRAD)

        pos = Point(
            start.x + breite,  start.y - (höhe - quarter_height))
        next_pos = Point(start.x + breite,  start.y - breite / 2)
        self.draw_line(pos, next_pos)

        pos = Point(start.x + breite / 2,  start.y - quarter_height)
        self.draw_circle(breite / 2, quarter_height,
                         pos, 0, 2 * NEUNZIG_GRAD)
        self.stift_hoch()

    def draw_number_zero(self, start, height, width):
        pos = Point(start.x + width / 2,
                    start.y - 3 * quarter_height)
        self.draw_circle(width / 2, quarter_height, pos,
                         2 * NEUNZIG_GRAD, 4 * NEUNZIG_GRAD)

        pos = Point(start.x + width,  start.y - 3 * quarter_height)
        next_pos = Point(start.x + width,  start.y - quarter_height)
        self.draw_line(pos, next_pos)

        pos = Point(start.x + width / 2,  start.y - quarter_height)
        self.draw_circle(width / 2, quarter_height,
                         pos, 0, 2 * NEUNZIG_GRAD)

        pos = Point(start.x,  start.y - quarter_height)
        next_pos = Point(start.x,  start.y - 3 * quarter_height)
        self.draw_line(pos, next_pos)
        self.stift_hoch()

    def draw_number(self, start, number):
        number_painter = [self.draw_number_zero, self.draw_number_one, self.draw_number_two,
                          self.draw_number_three, self.draw_number_four, self.draw_number_five,
                          self.draw_number_six, self.draw_number_seven, self.draw_number_eight,
                          self.draw_number_nine]
        number_painter[number](start, real_height, real_width)

    def draw_doppelpunkt(self, start):
        pos = Point(start.x + (spacing / 2),
                    start.y + (1 / 3) * real_height)

        self.move_arms_to(pos)
        self.stift_runter()
        self.stift_hoch()

        pos.y += 1/3 * real_height
        self.move_arms_to(pos)
        self.stift_runter()
        self.stift_hoch()

    def draw_time_from_str(self, timestr):
        timestr = ('0'+timestr)[-5:]
        start = Point(sandbox_start.x, sandbox_start.y)
        self.draw_number(start, int(timestr[0]))
        start.x += real_width + spacing
        self.draw_number(start, int(timestr[1]))
        start.x += real_width + spacing
        self.draw_doppelpunkt(start)
        start.x += spacing
        self.draw_number(start, int(timestr[3]))
        start.x += real_width + spacing
        self.draw_number(start, int(timestr[4]))
        self.move_arms(3 * NEUNZIG_GRAD / 2, NEUNZIG_GRAD / 2)
        