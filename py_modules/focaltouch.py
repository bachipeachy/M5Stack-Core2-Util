# The MIT License (MIT)
#
# Copyright (c) 2017 ladyada for adafruit industries
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
The original software by Adafruit at
https://github.com/adafruit/Adafruit_CircuitPython_FocalTouch/blob/main/adafruit_focaltouch.py
is extensively modified/extended by bachipeachy@gmail.com to add additional features and
tested exclusively on M5Stack Core 2 Hardware. Software may be adopted for other hardware.
The enhanced features include:
1) Support for swipe gestures -- 'LEFT', 'RIGHT', 'UP' and 'DOWN' in addition to
2) Support for touch gestures -- "TAP" and "HELD" gestures for a single touch opeqrtion
3) Support for tunable parameters for various gestures to address granularity and speed of response.

Although, the FocalTouch FT-62XX advertizes support for multitouch, it seems, at least on
M5Stack Core2 test hardware multi-touch (two finger gestures) does not work satisfatorily as a
result multtouch gestures such as pinch, expand, rotate could not be implemented.
The multitouch sensor seems to work correctly for changes in 'y' co-ordinates but did not responsd for 'x'.
"""

import math
import struct
from micropython import const

_FT6206_DEFAULT_I2C_ADDR = 0x38
_FT6XXX_REG_DATA = const(0x00)
_FT6XXX_REG_NUMTOUCHES = const(0x02)
_FT6XXX_REG_THRESHHOLD = const(0x80)
_FT6XXX_REG_POINTRATE = const(0x88)
_FT6XXX_REG_LIBH = const(0xA1)
_FT6XXX_REG_LIBL = const(0xA2)
_FT6XXX_REG_CHIPID = const(0xA3)
_FT6XXX_REG_FIRMVERS = const(0xA6)
_FT6XXX_REG_VENDID = const(0xA8)
_FT6XXX_REG_RELEASE = const(0xAF)


class FocalTouch:
    """ 'single touch gestures' driver for M5Stack Focaltouch capacitive touch sensor """

    def __init__(self, i2c, btns, address=_FT6206_DEFAULT_I2C_ADDR, debug=False,
                 touched_th=25, held_th=250, delta_x_th=32, delta_y_th=24):

        self.i2c = i2c
        if btns is None:
            self.btns = {'screen': {'loc': (0, 0, 320, 240)}}
        else:
            self.btns = btns
        self.address = address
        self.debug = debug

        self.touched_th = touched_th
        self.held_th = held_th
        self.delta_x_th = delta_x_th
        self.delta_y_th = delta_y_th

        chip_data = self._read(_FT6XXX_REG_LIBH, 8)
        lib_ver, chip_id, _, _, firm_id, _, vend_id = struct.unpack(">HBBBBBB", chip_data)
        self.vend_id = vend_id
        if chip_id == 0x06:
            self.chip = "FT6206"
        elif chip_id == 0x64:
            self.chip = "FT6236"
        else:
            self.chip = "UNKNOWN"

        if debug:
            print("{}{} -> hardware info ..".format(FocalTouch, FocalTouch.__init__))
            print("Vendor ID %02x" % vend_id)
            print("Chip Id: %02x" % chip_id)
            print("chip model: ", self.chip)
            print("Library vers %04X" % lib_ver)
            print("Firmware ID %02X" % firm_id)
            print("Point rate %d Hz" % self._read(_FT6XXX_REG_POINTRATE, 1)[0])
            print("Thresh %d" % self._read(_FT6XXX_REG_THRESHHOLD, 1)[0])
        print("* touch screen chip type is ", self.chip)

    def _read(self, reg, length):
        """ returns an array of 'length' bytes from the 'register' """

        result = bytearray(length)
        self.i2c.readfrom_mem_into(self.address, reg, result)
        # print("from _read reg#{} -> {}".format(reg, [i for i in result]))
        return result

    def _write(self, reg, values):
        """ writes an array of 'length' bytes to the 'register' """

        values = [(v & 0xFF) for v in values]
        self.i2c.writeto_mem(self.address, reg, bytes(values))
        # print("from _write reg#{} -> {}".format(reg, [i for i in values]))

    def _endpoints(self):
        """ returns scan cycle count and two end points of a single touch/hold/swipe action """

        e_pts = [None, None]
        ep = None
        scans = 0

        try:
            while self.touch_count:
                ep = self.touch_points[0]
                if scans == 0:
                    e_pts[0] = ep
                scans = scans + 1

        except IndexError as e:
            # print("{} -- ignoring '_endpoints' nuisance error".format(e))
            pass

        if ep is not None:
            e_pts[1] = ep

        return scans, e_pts

    def _angle(self, e_pts):
        """ returns angle of swipe 0 - 360 range """

        if e_pts[0]['id'] == e_pts[1]['id'] == 0:
            x1 = e_pts[0]['x']
            y1 = e_pts[0]['y']
            x2 = e_pts[1]['x']
            y2 = e_pts[1]['y']
            rad = math.atan2(y1 - y2, x2 - x1) + 3.14
            deg = int((rad * 180 / 3.14 + 180) % 360)
            if self.debug:
                print("* swipe angle: {}".format(deg))
            return deg

    @staticmethod
    def _vector(deg):
        """
        returns computed direction of swap
        acknowledgement: algoithm explained in https://stackoverflow.com/questions/13095494/
        """

        up = range(45, 135)
        left = range(135, 225)
        down = range(225, 315)
        right1 = range(315, 360)
        right2 = range(0, 45)

        if deg in up:
            return "UP"
        elif deg in left:
            return "LEFT"
        elif deg in down:
            return "DOWN"
        elif deg in right1 or deg in right2:
            return "RIGHT"
        else:
            return "IGNORE"

    def _gesture(self):
        """ returns gesture action type -- 'TAP', 'HOLD', 'LEFT', 'RIGHT', 'UP', 'DOWN','IGNORE' or 'NONE'  """

        scans, e_pts = self._endpoints()

        if e_pts[0] is not None:

            dx = abs(e_pts[0]['x'] - e_pts[1]['x'])
            dy = abs(e_pts[0]['y'] - e_pts[1]['y'])

            if dx > self.delta_x_th or dy > self.delta_y_th:
                deg = self._angle(e_pts)
                vector = self._vector(deg)
                if self.debug and vector is not "IGNORE":
                    print("* {} swipe -- because dx:{}>{} OR dy:{}>{}".format(
                        vector, dx, self.delta_x_th, dy, self.delta_y_th))
                return vector

            elif scans > self.held_th:
                if self.debug:
                    print("* HOLD -- because {} is greater than {},"
                          "checking for swipe indicated by dx:{}<{} and dy:{}<{}"
                          .format(scans, self.held_th, dx, self.delta_x_th, dy, self.delta_y_th))
                return "HOLD"

            elif scans > self.touched_th:
                if self.debug:
                    print("* TAP -- because {} is in between {} and {}".format(
                        scans, self.touched_th, self.held_th))
                return "TAP"

    @property
    def touch_count(self):
        """ returns single finger touch =1, two finger touch = 2 and no touch detected = 0  """

        return self._read(_FT6XXX_REG_NUMTOUCHES, 1)[0]

    @property
    def touch_points(self):
        """
        returns a list of touchpoint dicts, with 'x' and 'y' containing the
        touch coordinates, and 'id' as the touch # for multitouch tracking
        """

        touchpoints = []
        data = self._read(_FT6XXX_REG_DATA, 32)

        for i in range(2):
            point_data = data[i * 6 + 3: i * 6 + 9]
            if all([i == 0xFF for i in point_data]):
                continue
            # print([hex(i) for i in point_data])
            x, y, weight, misc = struct.unpack(">HHBB", point_data)
            # print(x, y, weight, misc)
            touch_id = y >> 12
            x &= 0xFFF
            y &= 0xFFF
            point = {"x": x, "y": y, "id": touch_id}
            touchpoints.append(point)
        return touchpoints

    def touch_detected(self, loc=(0, 0, 320, 240)):
        """ return True/False/None if a single touch is detected within the specified loc """

        x, y = None, None

        try:
            x = self.touch_points[0]['x']
            y = self.touch_points[0]['y']

            if (loc[0] <= x <= loc[0] + loc[2]
                    and loc[1] <= y <= loc[1] + loc[3]):
                return True
            else:
                return False

        except IndexError as e:
            # print("{} -- ignoring 'loc_touched' nuisance error".format(e))
            pass

    def btn_gesture(self):
        """ returns the touched btn from a dict of btns with gesture 'action' added"""

        for k, v in self.btns.items():
            if self.touch_detected(v['loc']):
                ges = self._gesture()
                if ges is not None and ges is not "IGNORE":
                    btn = {k: {'loc': v['loc'], 'action': ges}}
                    print("# gestured -> {}".format(btn))
                    return btn
        return None
