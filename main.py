from machine import Pin, I2C
from binascii import hexlify
from time import sleep
import math

from pca9685 import PCA9685
from sanduhr import Point, Sanduhr

i2c = I2C(scl=Pin(5), sda=Pin(4), freq=100000)

ports = i2c.scan()
print(ports)

# reset all devices
i2c.writeto(0, b'\x06')

i2c.stop()

pca = PCA9685()

pca.frequeny = 50

lift_arm = 13
left_arm = 14
right_arm = 15

pca.init_servo(left_arm, 400, 2100, 225)
pca.init_servo(right_arm, 420, 1700, 225)

# for angle in range(0,181,45):
    # pca.set_angle(left_arm, angle)
#    pca.set_angle(right_arm, angle)

#    sleep(2)

# pca.set_angle(left_arm, 90)
# pca.set_angle(right_arm, 90)

# sleep(2)


clock = Sanduhr(pca, left_arm, right_arm, lift_arm)

clock.draw_time(1, 2,3,4)
sleep(2)
clock.move_arms(math.pi/2, math.pi/2)

