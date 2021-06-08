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
SERVO1_POS = Point(390, 50)
SERVO2_POS = Point(610, 50)
SANDBOX_START = Point(170, 580)

# Länge der Arme im Koordinatensystem
LENGTH_ARM_A = 320
LENGTH_ARM_B = 400

NEUNZIG_GRAD = math.pi / 2

CIRCLE_STEP = 1
# Breite einer Ziffer
FULL_WIDTH = 110
# Höhe einer Ziffer
FULL_HEIGHT = 230.0
HALF_HEIGHT = FULL_HEIGHT / 2
QUARTER_HEIGHT = FULL_HEIGHT / 4

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
        self.position = Point(
            SANDBOX_START.x + (2 * FULL_WIDTH) + (3 * spacing),
            SANDBOX_START.y - HALF_HEIGHT
        )
        self.move_arms_to(self.position)

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
                (LENGTH_ARM_A ** 2 + BD ** 2 - LENGTH_ARM_B ** 2)
                / (2 * LENGTH_ARM_A * BD)
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
                (LENGTH_ARM_A ** 2 + AD ** 2 - LENGTH_ARM_B ** 2)
                / (2 * LENGTH_ARM_A * AD)
            )  # Kosinussatz
            alpha = r1 + w1
            if AR < 0:
                alpha = (NEUNZIG_GRAD * 2 - r1) + w1

        return alpha

    def move_arms_to(self, ende):
        alpha = self.calculate_angle(SERVO1_POS, ende, 1)
        beta = self.calculate_angle(SERVO2_POS, ende, 2)
        self.move_arms(alpha, beta)

    def draw_line_to(self, end):
        if (end.y >= self.position.y):
            a = self.position.y - end.y
        else:
            a = end.y - self.position.y

        if (self.position.x >= end.x):
            b = end.x - self.position.x
        else:
            b = end.x - self.position.x

        c = math.sqrt((a ** 2) + (b ** 2))

        abstand = FULL_HEIGHT / 60
        angle = math.acos(b / c)

        if (self.position.y > end.y):
            angle = 2 * math.pi - angle

        self.move_arms_to(self.position)
        for actual_abstand in frange(abstand, c, abstand):
            ende = self.end_from_angle(self.position, angle, actual_abstand)
            self.move_arms_to(ende)

        self.move_arms_to(end)
        self.position = end

    def draw_circle(self, radius_x, radius_y, mittelpunkt, start_winkel, end_winkel):
        # die erste Position wird mit Stift_hoch angefahren
        for winkel in frange(start_winkel, end_winkel, NEUNZIG_GRAD / 20):
            pos = self.end_from_angle(mittelpunkt, winkel, radius_x)
            #  skalieren, damit es ein Oval wird
            pos.y = mittelpunkt.y + \
                (pos.y - mittelpunkt.y) * (radius_y / radius_x)

            self.draw_line_to(pos)
            # nach erster Position Stift runter für weiteren Kreis
            self.stift_runter()

        pos = self.end_from_angle(mittelpunkt, winkel, radius_x)
        #  skalieren, damit es ein Oval wird
        pos.y = mittelpunkt.y + (pos.y - mittelpunkt.y) * (radius_y / radius_x)

        self.draw_line_to(pos)

    def draw_number_one(self, start):
        self.draw_line_to(Point(start.x, start.y - (2 / 3 * FULL_HEIGHT)))
        self.stift_runter()
        self.draw_line_to(Point(start.x + FULL_WIDTH, start.y - FULL_HEIGHT))
        self.draw_line_to(Point(start.x + FULL_WIDTH, start.y))
        self.stift_hoch()

    def draw_number_two(self, start):
        pos = Point(start.x + FULL_WIDTH / 2,
                    start.y - (FULL_HEIGHT - QUARTER_HEIGHT))
        # draw_circle macht den Stift runter
        self.draw_circle(FULL_WIDTH / 2, QUARTER_HEIGHT, pos,
                         2 * NEUNZIG_GRAD, 4 * NEUNZIG_GRAD)
        pos = Point(start.x + FULL_WIDTH, start.y - (FULL_HEIGHT - QUARTER_HEIGHT))
        self.draw_line_to(start)
        pos = Point(start.x + FULL_WIDTH, start.y)
        self.draw_line_to(pos)
        self.stift_hoch()

    def draw_number_three(self, start):
        pos = Point(start.x + FULL_WIDTH / 2,
                    start.y - FULL_HEIGHT + QUARTER_HEIGHT)
        # draw_circle macht den Stift runter
        self.draw_circle(FULL_WIDTH / 2, QUARTER_HEIGHT, pos,
                         2 * NEUNZIG_GRAD, 5 * NEUNZIG_GRAD)

        pos = Point(start.x + FULL_WIDTH / 2, start.y - QUARTER_HEIGHT)
        self.draw_circle(FULL_WIDTH / 2, QUARTER_HEIGHT, pos,
                         3 * NEUNZIG_GRAD, 6 * NEUNZIG_GRAD)
        self.stift_hoch()

    def draw_number_four(self, start):
        self.draw_line_to(Point(start.x + FULL_WIDTH,     start.y - (FULL_HEIGHT * 0.4)))
        self.stift_runter()
        self.draw_line_to(Point(start.x,                  start.y - (FULL_HEIGHT * 0.4)))
        self.draw_line_to(Point(start.x + FULL_WIDTH / 2, start.y - FULL_HEIGHT))
        self.stift_hoch()
        self.draw_line_to(Point(start.x + FULL_WIDTH / 2, start.y - (FULL_HEIGHT * 0.6)))
        self.stift_runter()
        self.draw_line_to(Point(start.x + FULL_WIDTH / 2, start.y))
        self.stift_hoch()

    def draw_number_five(self, start):
        self.draw_line_to(Point(start.x + FULL_WIDTH,     start.y - FULL_HEIGHT))
        self.stift_runter()
        self.draw_line_to(Point(start.x,                  start.y - FULL_HEIGHT))
        self.draw_line_to(Point(start.x,                  start.y - HALF_HEIGHT))
        self.draw_line_to(Point(start.x + FULL_WIDTH / 2, start.y - HALF_HEIGHT))
        next_pos = Point(start.x + FULL_WIDTH / 2,        start.y - QUARTER_HEIGHT)
        self.draw_circle(FULL_WIDTH / 2, QUARTER_HEIGHT, next_pos,
                         3 * NEUNZIG_GRAD, 6 * NEUNZIG_GRAD)
        self.stift_hoch()

    def draw_number_six(self, start):
        pos = Point(start.x + FULL_WIDTH / 2,  start.y - QUARTER_HEIGHT)
        self.draw_circle(FULL_WIDTH / 2, QUARTER_HEIGHT,
                         pos, 0, 4 * NEUNZIG_GRAD)

        self.draw_line_to(Point(start.x,  start.y - (3 * QUARTER_HEIGHT)))

        pos = Point(start.x + FULL_WIDTH / 2,
                    start.y - (FULL_HEIGHT - QUARTER_HEIGHT))
        self.draw_circle(FULL_WIDTH / 2, QUARTER_HEIGHT, pos,
                         2 * NEUNZIG_GRAD, 4 * NEUNZIG_GRAD)
        self.stift_hoch()

    def draw_number_seven(self, start):
        self.draw_line_to(Point(start.x,               start.y - FULL_HEIGHT))
        self.stift_runter()
        self.draw_line_to(Point(start.x + FULL_WIDTH,  start.y - FULL_HEIGHT))
        self.draw_line_to(start)
        self.stift_hoch()
        self.draw_line_to(Point(start.x,               start.y - HALF_HEIGHT))
        self.stift_runter()
        self.draw_line_to(Point(start.x + FULL_WIDTH,  start.y - HALF_HEIGHT))
        self.stift_hoch()

    def draw_number_eight(self, start):
        pos = Point(start.x + FULL_WIDTH / 2,  start.y - QUARTER_HEIGHT)
        self.draw_circle(FULL_WIDTH / 2, QUARTER_HEIGHT,
                         pos, 
                         3 * NEUNZIG_GRAD, 7 * NEUNZIG_GRAD)
        pos.y -= HALF_HEIGHT
        self.draw_circle(FULL_WIDTH / 2, QUARTER_HEIGHT,
                         pos, 
                         1 * NEUNZIG_GRAD, 5 * NEUNZIG_GRAD)
        self.stift_hoch()

    def draw_number_nine(self, start):

        pos = Point(start.x + FULL_WIDTH / 2,
                    start.y - (FULL_HEIGHT - QUARTER_HEIGHT))

        self.draw_circle(FULL_WIDTH / 2, QUARTER_HEIGHT,
                         pos, 0, 4 * NEUNZIG_GRAD)

        self.draw_line_to(Point(start.x + FULL_WIDTH,  start.y - FULL_WIDTH / 2))

        pos = Point(start.x + FULL_WIDTH / 2,  start.y - QUARTER_HEIGHT)
        self.draw_circle(FULL_WIDTH / 2, QUARTER_HEIGHT,
                         pos, 0, 2 * NEUNZIG_GRAD)
        self.stift_hoch()

    def draw_number_zero(self, start):
        pos = Point(start.x + FULL_WIDTH / 2,
                    start.y - 3 * QUARTER_HEIGHT)
        self.draw_circle(FULL_WIDTH / 2, QUARTER_HEIGHT, pos,
                         2 * NEUNZIG_GRAD, 4 * NEUNZIG_GRAD)
        self.draw_line_to(Point(start.x + FULL_WIDTH,  start.y - QUARTER_HEIGHT))

        pos = Point(start.x + FULL_WIDTH / 2,  start.y - QUARTER_HEIGHT)
        self.draw_circle(FULL_WIDTH / 2, QUARTER_HEIGHT,
                         pos, 0, 2 * NEUNZIG_GRAD)
        self.draw_line_to(Point(start.x,  start.y - 3 * QUARTER_HEIGHT))
        self.stift_hoch()

    def draw_number(self, start, number):
        number_painter = [self.draw_number_zero, self.draw_number_one, self.draw_number_two,
                          self.draw_number_three, self.draw_number_four, self.draw_number_five,
                          self.draw_number_six, self.draw_number_seven, self.draw_number_eight,
                          self.draw_number_nine]
        number_painter[number](start)

    def draw_doppelpunkt(self, start):
        pos = Point(start.x + (spacing / 2), start.y - (1 / 3) * FULL_HEIGHT)
        self.draw_line_to()
        self.stift_runter()
        self.stift_hoch()

        pos.y -= 1/3 * FULL_HEIGHT
        self.draw_line_to(pos)
        self.stift_runter()
        self.stift_hoch()

    def draw_time_from_str(self, timestr):
        timestr = ('0'+timestr)[-5:]
        start = Point(SANDBOX_START.x, SANDBOX_START.y)
        self.draw_number(start, int(timestr[0]))
        start.x += FULL_WIDTH + spacing
        self.draw_number(start, int(timestr[1]))
        start.x += FULL_WIDTH + spacing
        self.draw_doppelpunkt(start)
        start.x += spacing
        self.draw_number(start, int(timestr[3]))
        start.x += FULL_WIDTH + spacing
        self.draw_number(start, int(timestr[4]))
        self.move_arms(3 * NEUNZIG_GRAD / 2, NEUNZIG_GRAD / 2)
