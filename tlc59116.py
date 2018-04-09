"""
    TLC59116 Driver
    Scott Baker, smbaker@smbaker.com
"""

import sys

REG_MODE1 = 0
REG_MODE2 = 1
REG_GRPPWM = 0x12
REG_GRPFREQ = 0x13
REG_LEDOUT0 = 0x14

MODE1_OSC_OFF = 16
MODE1_ALL_CALL = 1

MODE2_DMBLNK = 0x20

STATE_OFF = 0
STATE_ON = 1
STATE_PWM = 2
STATE_GRP = 3

class TLC59116(object):
    def __init__(self, bus, addr):
        self.addr = addr
        self.bus = bus
        self.mode1 = self.read_reg(REG_MODE1) #default: MODE1_OSC_OFF | MODE1_ALL_CALL
        self.mode2 = self.read_reg(REG_MODE2) #detault: 0

    def read_reg(self, reg):
        return self.bus.read_byte_data(self.addr, reg)

    def write_reg(self, reg, bits):
        self.bus.write_byte_data(self.addr, reg, bits)

    def set_oscillator(self, enable):
        if enable:
            self.mode1 = self.mode1 & (~MODE1_OSC_OFF)
        else:
            self.mode1 = self.mode1 | MODE1_OSC_OFF
        self.write_reg(REG_MODE1, self.mode1)

    def set_led_state(self, led, state):
        reg = (led / 4) + REG_LEDOUT0
        shift = (led % 4) * 2
        print shift, state<<shift
        v = self.read_reg(reg)
        v = v & (~(3 << shift)) | (state << shift)
        print "write mode reg %x %x" % (reg, v)
        self.write_reg(reg, v)

    def set_led_pwm(self, led, brightness):
        self.write_reg(led+2, brightness)

    def set_blink(self, blink):
        if blink:
            self.mode2 = self.mode2 | MODE2_DMBLNK
        else:
            self.mode2 = self.mode2 & (~MODE2_DMBLNK)
        self.write_reg(REG_MODE2, self.mode2)

    def set_grpfreq(self, freq):
        self.write_reg(REG_GRPFREQ, freq)

    def set_grppwm(self, freq):
        self.write_reg(REG_GRPPWM, freq)

def help():
    print "tcl59116.py <command> <args>"
    print
    print "commands:"
    print "    led <num> [off|on|pwm|grp] <pwmval>"
    print "    blink <rate>"
    print "    noblink"
    print "    grppwm <pwmval>"

def main():
    import smbus

    bus = smbus.SMBus(1)
    leds = TLC59116(bus, 0x60)

    if (len(sys.argv) <= 1):
        help()
        sys.exit(0)

    if (sys.argv[1] == "led"):
        led = int(sys.argv[2])
        mode = sys.argv[3]

        if (mode=="off"):
            mode = STATE_OFF
        elif (mode=="on"):
            mode = STATE_ON
        elif (mode=="pwm"):
            mode = STATE_PWM
        elif (mode=="grp"):
            mode = STATE_GRP
        else:
            raise Exception("unknown mode")

        pwm = int(sys.argv[4])

        leds.set_oscillator(True)
        leds.set_led_state(led, mode)
        leds.set_led_pwm(led, pwm)
    elif (sys.argv[1] == "blink"):
        leds.set_blink(True)
        leds.set_grppwm(128)
        leds.set_grpfreq(int(sys.argv[2]))
    elif (sys.argv[1] == "noblink"):
        leds.set_blink(False)
        leds.set_grppwm(255)
    elif (sys.argv[1] == "grppwm"):
        leds.set_blink(False)
        leds.set_grppwm(int(sys.argv[2]))
    else:
        help()


if __name__ == "__main__":
    main()
