"""
The MIT License (MIT)

Copyright (c) 2022 bachipeachy@gmail.com

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import errno
import time

import axp202c
import ili9342c
import network
import uos
import vga1_16x16 as font16
import vga1_8x8 as font8
from esp32 import raw_temperature, hall_sensor
from focaltouch import FocalTouch
from machine import SoftI2C, Pin, SPI, soft_reset, reset
from mpu6886 import MPU6886, SF_DEG_S
from sdcard import SDCard


class M5core2:
    btn_a = {'loc': (3, 240, 102, 40), 'lbl': 'BtnA'}
    btn_b = {'loc': (109, 240, 102, 40), 'lbl': 'BtnB'}
    btn_c = {'loc': (215, 240, 102, 40), 'lbl': 'BtnC'}

    btn_t = {'loc': (0, 0, 320, 32), 'lbl': 'BtnT', 'fg': ili9342c.YELLOW, 'bg': ili9342c.BLACK}
    btn_w = {'loc': (0, 32, 320, 176), 'lbl': 'BtnW', 'fg': ili9342c.BLACK, 'bg': ili9342c.BLACK}

    btn_1 = {'loc': (0, 208, 78, 32), 'lbl': 'Btn1', 'fg': ili9342c.YELLOW, 'bg': ili9342c.BLUE}
    btn_2 = {'loc': (80, 208, 78, 32), 'lbl': 'Btn2', 'fg': ili9342c.YELLOW, 'bg': ili9342c.BLUE}
    btn_3 = {'loc': (160, 208, 78, 32), 'lbl': 'Btn3', 'fg': ili9342c.YELLOW, 'bg': ili9342c.BLUE}
    btn_4 = {'loc': (240, 208, 78, 32), 'lbl': 'Btn4', 'fg': ili9342c.YELLOW, 'bg': ili9342c.BLUE}

    btn_5 = {'loc': (0, 0, 78, 32), 'lbl': 'Btn4', 'fg': ili9342c.YELLOW, 'bg': ili9342c.BLUE}
    btn_6 = {'loc': (80, 0, 78, 32), 'lbl': 'Btn5', 'fg': ili9342c.YELLOW, 'bg': ili9342c.BLUE}
    btn_7 = {'loc': (160, 0, 78, 32), 'lbl': 'Btn6', 'fg': ili9342c.YELLOW, 'bg': ili9342c.BLUE}
    btn_8 = {'loc': (240, 0, 78, 32), 'lbl': 'Btn7', 'fg': ili9342c.YELLOW, 'bg': ili9342c.BLUE}

    def __init__(self, essid=None, pwd=None, mdir='/sd', imu_samples=10, imu_wait=100):
        """ auto start power up, touch and tft services """

        if essid is None:
            print("Missing wireless ssid ..")
        self.essid = essid
        if pwd is None:
            print("Missing wireless password ..")
        self.pwd = pwd

        self.mdir = mdir
        self.imu_samples = imu_samples
        self.imu_wait = imu_wait

        self.i2c = SoftI2C(scl=Pin(22), sda=Pin(21))
        self.axp = self.power_up()
        self.spi2 = SPI(2, sck=Pin(18), mosi=Pin(23), miso=Pin(38))
        self.sensor = MPU6886(self.i2c, gyro_sf=SF_DEG_S)
        self.tft = self.enable_tft()

        self.greet()
        print("* M5Stack Core2 initialization complete")

        self.touch = None
        self.btns = {'btn_a': M5core2.btn_a, 'btn_b': M5core2.btn_b, 'btn_c': M5core2.btn_c,
                     'btn_t': M5core2.btn_t, 'btn_w': M5core2.btn_w}
        
        self.add_appbtns()
        self.update_clock(dt=True)

    def power_up(self):
        """ turn on M5Stack Core2 """

        axp = axp202c.PMU(i2c=self.i2c, address=0x34)
        axp.enablePower(axp202c.AXP192_LDO2)
        axp.setDC3Voltage(3000)
        print("* M5Core2 powered up")
        return axp

    @staticmethod
    def soft_reset():
        print("* soft reset")
        soft_reset()

    @staticmethod
    def hard_reset():
        print("* hard reset")
        reset()

    def power_down(self):
        """ turn off M5Stack Core2 """

        print("* M5Core2 shutting it down ..")
        time.sleep(2)
        self.axp.shutdown()

    def enable_tft(self):
        """ initialize tft function for display """

        tft = ili9342c.ILI9342C(
            self.spi2,
            320, 240,
            reset=Pin(33, Pin.OUT),
            cs=Pin(5, Pin.OUT),
            dc=Pin(15, Pin.OUT),
            rotation=0)
        tft.init()
        print("* tft display enabled")
        return tft

    def enable_touch(self):
        """ enable touch with current btns passed as parm """

        touch = FocalTouch(self.i2c, self.btns)
        print("* touch enabled {} btns with {}".format(len(self.btns), self.btns.keys()))
        return touch

    def mount_sd(self):
        """ mount the sdcard """
        try:
            sdc = SDCard()
            vfs = uos.VfsFat(sdc)
            uos.mount(vfs, self.mdir)
            print("Flash Memory root level listing -> {}\nSDCard root files {} -> {}".format(
                uos.listdir(), self.mdir, uos.listdir(self.mdir)))
        except OSError as e:
            if e.errno == errno.EPERM:
                print("{} already mounted".format(self.mdir))
        except Exception as e:
            print("ERROR: {}".format(e))

    def release_spi2(self):
        """ release spi channel for sharing """

        self.spi2.deinit()
        self.spi2.init()
        print("* released spi2")

    def greet(self):
        """ test initialization """

        # $self.erase_btns({'btn_t': self.btns['btn_t']})
        self.tft.text(font16, "M5Core2> initialized!", 0, 0, ili9342c.WHITE, ili9342c.BLACK)

    def add_appbtns(self):
        self.add_btn('btn_1', M5core2.btn_1)
        self.add_btn('btn_2', M5core2.btn_2)
        self.add_btn('btn_3', M5core2.btn_3)
        self.add_btn('btn_4', M5core2.btn_4)

    def paint_btn(self, v):
        
        self.tft.fill_rect(v['loc'][0], v['loc'][1], v['loc'][2], v['loc'][3], v['bg'])
        self.tft.text(font16, v['lbl'], v['loc'][0] + 4, v['loc'][1] + 8, v['fg'], v['bg'])

    def erase_btn(self, v):

        self.tft.fill_rect(v['loc'][0], v['loc'][1], v['loc'][2], v['loc'][3], ili9342c.BLACK)

    def add_btn(self, k, v):

        print("* adding btn {} ".format(k))
        if k not in self.btns.keys():
            self.paint_btn(v)
            self.btns.update({k: v})
            self.touch = self.enable_touch()
        else:
            print("* warning {} exists in self.btns".format(k))

    def delete_btn(self, k, v):

        if k in self.btns.keys():
            print("* deleting  {} ".format(k))
            del self.btns[k]
            self.erase_btn(v)
            self.touch = self.enable_touch()
        else:
            print("* warning no such {} to delete in self.btns".format(k))

    def write(self, tl, f=font8, xl=None, yl=None, fg=None, bg=None):
        """ write txt from a list at x,y coordinates in a list"""

        if xl is None:
            xl = [0]
        if yl is None:
            yl = [40]
        if fg is None:
            fg = ili9342c.WHITE
        if bg is None:
            bg = ili9342c.BLACK

        [self.tft.text(f, t, xl[i], yl[i], fg, bg) for i, t in enumerate(tl)]

    def update_clock(self, dt=None):
        """ update btn_t wk_dt_time display"""
        # display format: Tue Apr 02, 10:05:02
        # time.localtime() returns (yr, mo, day, hr, mi, se, wd, yd)

        wd = ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')
        mo = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')

        t = time.localtime()
        h = str(t[3]) if t[3] > 9 else '0' + str(t[3])
        m = str(t[4]) if t[4] > 9 else '0' + str(t[4])
        s = str(t[5]) if t[5] > 9 else '0' + str(t[5])
        hms = h + ':' + m + ':' + s

        if dt is not None:
            self.erase_btn(M5core2.btn_t)
            tl = [wd[t[6]], mo[t[1] - 1], str(t[2]) + ', ', hms]
            xl = [0, 64, 128, 192]
            yl = [4, 4, 4, 4]
        else:
            self.tft.fill_rect(176, 0, 144, 32, ili9342c.BLACK)
            tl = [hms]
            xl = [192]
            yl = [4]

        self.write(f=font16, tl=tl, xl=xl, yl=yl, fg=ili9342c.YELLOW)
        print("* updated clock -> ", hms, t)
        return t

    @staticmethod
    def is_wifi_connected():
        """ returns True or False of wifi connection status """

        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        print("wifi connection active -> {}".format(wlan.isconnected()))
        return wlan.isconnected()

    def connect_wifi(self):
        """ connect wifi if disconnected """

        wlan = network.WLAN(network.STA_IF)
        t1 = time.time()
        run = True
        wlan.active(True)
        i = 15
        if not wlan.isconnected():
            print("connecting to wireless '{}' with {} sec timeout ...".format(self.essid, i))

            try:
                wlan.connect(self.essid, self.pwd)
            except Exception as e:
                print("ERROR: {} .. check or missing/wrong essid/pwd info\n Stand by ..".format(e))

            while not wlan.isconnected() and run:
                if (time.time() - t1) > i:
                    run = False
        else:
            print("wifi connection active -> {}".format(wlan.ifconfig()[0]))
            return wlan.ifconfig()[0]

        if run:
            print("wifi connection established -> {}".format(wlan.ifconfig()[0]))
        else:
            print("unable to connect to SSID-> '{}'".format(self.essid))

        return wlan.ifconfig()[0]

    @staticmethod
    def disconnect_wifi():
        """ disconnect wifi if connected """

        wlan = network.WLAN(network.STA_IF)
        wlan.active(False)
        print("wifi disconnected -> {}".format(wlan.ifconfig()[0]))
        return wlan.ifconfig()[0]

    @staticmethod
    def scan_wifi():
        """ scan wlan to extract ssid and RSSI """
        """
        wifi list will have 2 of 6 tuples -- 'ssid, bssid, ch, RSSI, auth and hidden'
        # RSSI - Received Signal Strength Indicator
        Excellent -33 to -67  4 bars green
        Good      -67 to -70  3 bars blue
        OK        -70 to -80  2 bars yellow
        Bad       -80 to -90   1 bar  red
        """

        bar4 = -67
        bar3 = -78
        bar2 = 80

        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        print("scanning wifi ..")
        vals = wlan.scan()

        lines = []
        for i, v in enumerate(vals):
            ssid = v[0]
            rssi = v[3]
            if rssi >= bar4:
                bars = 4
            elif rssi >= bar3:
                bars = 3
            elif rssi >= bar2:
                bars = 2
            else:
                bars = 1
            lines.append((ssid, rssi, bars))

        print("wifi scanned {} essid's".format(len(lines)))
        return lines

    def read_imu(self):
        """  returns a dict of id, timestamp and readings as a list of 3-values tuple & uom, and temp """

        imu = {'id': self.sensor.whoami,
               'ts': [time.time_ns(), 'ns'],
               'accl': [self.sensor.acceleration, 'm/s/s'],
               'gyro': [self.sensor.gyro, 'deg/s'],
               'temp': round(self.sensor.temperature * 1.8 + 32, 1)}
        return imu

    def save_imu_scan(self):
        """ save IMU data after gyro calibration to SDCard for a given samples count and wait time as init parms """

        self.mount_sd()
        fn = self.mdir + "/imu_scan" + ".csv"
        with open(fn, "w") as f:
            header = "timestamp,accl_x,accl_y,accl_z,gyro_x,gyro_y,gyro_z,\n"
            f.write(header)
            gyro_offset = self.sensor.calibrate()
            print("gyro_offset -> {}".format(gyro_offset))
            print(header, end='')
            for n in range(self.imu_samples):
                ts = time.time_ns()
                accl = self.sensor.acceleration
                gyro = self.sensor.gyro
                line = str(ts) + ',' + str(accl[0]) + ',' + str(accl[1]) + ',' + str(accl[2]) \
                       + ',' + str(gyro[0]) + ',' + str(gyro[1]) + ',' + str(gyro[2]) + '\n'
                f.write(line)
                print(n + 1, '>', line, end='')
                time.sleep_ms(self.imu_wait)
        return gyro_offset

    @staticmethod
    def read_hall_sensor():
        """  returns a dict  of timestamp, 3d-readings and their uom """
        hs_val = {'ts': [time.time_ns(), 'ns'],
                  'hs': [hall_sensor(), 'micTes']}

        return hs_val

    @staticmethod
    def read_raw_temp():
        """  returns raw CPU temperature in def F """

        return round(raw_temperature(), 1)

    def erase_sd(self, path):
        """" on SDCard erase files and empty directories one at time """

        try:
            print("contents in sdcard before erase {} -> {}".format(self.mdir, uos.listdir(self.mdir)))

        except Exception as e:
            print("ERROR: {}".format(e))

        if path[0] != '/':
            path = '/' + path

        try:
            uos.remove(self.mdir + path)
            print("success removed'{}'".format(self.mdir + path))
            print("contents in sdcard after erase {} -> {}".format(self.mdir, uos.listdir(self.mdir)))

        except OSError as e:
            if e.errno == errno.ENOENT:
                print("ERRPR: {} erase failed did not find '{}'".format(e, self.mdir + path))
            else:
                print("checking if path '{}' is a dir".format(path))
            if e.errno == errno.EISDIR:
                try:
                    ct = len([f for f in uos.listdir(self.mdir + path)])
                    if ct == 0:
                        uos.rmdir(self.mdir + path)
                        print("success removed empty dir {}".format(self.mdir + path))
                        print("contents in sdcard after erase {} -> {}".format(self.mdir, uos.listdir(self.mdir)))
                    else:
                        print("{}: dir '{}' is not empty has {} entry -> {}".format(
                            e, self.mdir + path, ct, uos.listdir(self.mdir + path)))
                except Exception as e:
                    print("ERROR: {}".format(e))
            else:
                pass

        except Exception as e:
            print("ERROR: {}".format(e))


if __name__ == "__main__":
    
    m5 = M5core2(essid='TBD', pwd='????')
    m5.hard_reset()

