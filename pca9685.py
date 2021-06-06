from machine import Pin, I2C
class PCA9685:
    """
    16 units PWM output
    """
    min_values = [0 for i in range(16)]
    max_values = [4095 for i in range(16)]
    max_angles = [360 for i in range(16)]

    def _writeByte(self, register, value):
        self.i2c.writeto_mem(self.address, register, int(value).to_bytes(1, 'little'))

    def _writeRange(self, unit, on, off):
        self.i2c.writeto_mem(self.address, 4 * unit + 6, int(on).to_bytes(2, 'little') + int(off).to_bytes(2, 'little'))

    def __init__(self, i2c=None, address=0x40, reference_clock_speed=25000000):
        if i2c is None:
            i2c = I2C(scl=Pin(5), sda=Pin(4), freq=100000)
        self.i2c = i2c
        self.address = address
        self.reference_clock_speed = reference_clock_speed
        self.reset()

    def reset(self):
        """Reset the chip."""
        self.mode1_reg = b'\x20'

    @property
    def mode1_reg(self):
        return self.i2c.readfrom_mem(self.address, 0x00, 1)

    @mode1_reg.setter
    def mode1_reg(self, value):
        return self.i2c.writeto_mem(self.address, 0x00, value)


    @property
    def prescale_reg(self):
        return self.i2c.readfrom_mem(self.address, 0xfe, 1)

    @prescale_reg.setter
    def prescale_reg(self, value):
        # not supported
        return

    @property
    def frequency(self):
        """The overall PWM frequency in Hertz."""
        return self.reference_clock_speed / 4096 / self.prescale_reg

    @frequency.setter
    def frequency(self, freq):
        prescale = int(self.reference_clock_speed / 4096.0 / freq + 0.5)
        if prescale < 3:
            raise ValueError("PCA9685 cannot output at the given frequency")
        old_mode = self.mode1_reg  # Mode 1
        self.mode1_reg = (old_mode & 0x7F) | 0x10  # Mode 1, sleep
        self._writeByte(0xfe, prescale)  # Prescale
        self.mode1_reg = old_mode  # Mode 1
        time.sleep(0.005)
        self.mode1_reg = old_mode | 0xA1  # Mode 1, autoincrement on

    def set_pwm(self, unit, on, off):
        self._writeRange(unit, on, off)

    def init_servo(self, unit, min_val, max_val, max_angle):
        if unit < 0 or unit > 15:
            return
        if min_val < 0 or min_val > 4094:
            self.min_values[unit] = 0
        else:
            self.min_values[unit] = min_val

        if max_val <= self.min_values[unit] or max_val > 4095:
            self.max_values[unit] = 4095
        else:
            self.max_values[unit] = max_val
        
        if max_angle < 10:
            max_angle = 10
        
        if max_angle > 360:
            max_angle = 360

        self.max_angles[unit] = max_angle

    def set_angle(self, unit, angle):
        if unit < 0 or unit > 15:
            return
        if angle < 0:
            angle = 0
        if angle > self.max_angles[unit]:
            angle = self.max_angles[unit]

        switchpoint = self.min_values[unit] + (self.max_values[unit]-self.min_values[unit])*(float(angle)/self.max_angles[unit])
        # print(str(int(switchpoint))+' ', end='')

        self.set_pwm(unit, 0, int(switchpoint))
        
    def deinit(self):
        """Stop using the pca9685."""
        self.reset()