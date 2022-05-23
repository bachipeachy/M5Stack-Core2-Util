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
import ili9342c
import vga1_16x16 as font16
import vga1_8x8 as font8

from m5core2 import M5core2


class WifiApp:
    """ sample wifi app """

    def __init__(self, essid, pwd):
        """ run app forever until stopped hardware reset by middle hardware btn_b """

        self.essid = essid
        self.m5 = M5core2(essid=essid, pwd=pwd)

    def run_apps_forever(self):

        def app_help():
            self.m5.tft.text(font8, "display data: TAP/HOLD  WiFI btn", 32, 64, ili9342c.YELLOW, ili9342c.BLACK)
            self.m5.tft.text(font8, "shutdowm    : HOLD HW btn_a", 32, 80, ili9342c.YELLOW, ili9342c.BLACK)
            self.m5.tft.text(font8, "hard reboot : HOLD HW btn_b", 32, 96, ili9342c.YELLOW, ili9342c.BLACK)
            self.m5.tft.text(font8, "soft reboot : HOLD HW btn_c", 32, 112, ili9342c.YELLOW, ili9342c.BLACK)

        app_help()

        while True:
            touched_btn = self.m5.touch.btn_gesture()
            if touched_btn is not None:
                getattr(self, touched_btn['id'])(touched_btn)

    def btn_t(self, btn):
        self.m5.update_clock()

    def btn_w(self, btn):

        if btn["action"] == "LEFT" or 'RIGHT':
            print("Not Implemented ..")
        else:
            print("Not Implemented ..")

    def btn_1(self, btn):
        """ display scanned WiFi signal strengths and connect/disconnect chosen essid """

        self.m5.erase_window()
        count = 15
        loc = btn["loc"]

        def disconnect():
            print("disconnecting ..")
            _ = self.m5.disconnect_wifi()
            self.m5.tft.fill_rect(loc[0], loc[1], loc[2], loc[3], ili9342c.RED)
            self.m5.tft.text(font16, 'wifi', loc[0] + 8, loc[1] + 8, ili9342c.BLACK, ili9342c.RED)
            self.m5.tft.text(font16, "Wifi turned off", 48, 100, ili9342c.WHITE, ili9342c.BLACK)
            self.m5.tft.text(font16, "TAP to turn on", 48, 132, ili9342c.WHITE, ili9342c.BLACK)

        def scan():
            ls = self.m5.scan_wifi()
            if len(ls) > count:
                print("displaying first {} SSID's out of {} in range ..".format(count, len(ls)))
                header = "  SSID (" + str(count) + " of " + str(len(ls)) + ")  RSSI    signal bars"
                self.m5.tft.text(font8, header, 4, 36, ili9342c.YELLOW, ili9342c.BLACK)
            return ls

        def display(i, l):
            x1 = 2
            x2 = 162
            x3 = 194
            y = int(56 + i * 10)
            self.m5.tft.text(font8, l[0], x1, y, ili9342c.WHITE, ili9342c.BLACK)
            self.m5.tft.text(font8, str(l[1]), x2, y, ili9342c.WHITE, ili9342c.BLACK)
            bars = l[2]
            if bars > 0:
                self.m5.tft.fill_rect(x3, y, 30, 8, ili9342c.RED)
            if bars > 1:
                self.m5.tft.fill_rect(x3 + 32, y, 30, 8, ili9342c.YELLOW)
            if bars > 2:
                self.m5.tft.fill_rect(x3 + 64, y, 30, 8, ili9342c.BLUE)
            if bars > 3:
                self.m5.tft.fill_rect(x3 + 96, y, 30, 8, ili9342c.GREEN)

        def connect():
            print("connecting ..")
            _ = self.m5.connect_wifi()
            self.m5.tft.fill_rect(loc[0], loc[1], loc[2], loc[3], ili9342c.GREEN)
            self.m5.tft.text(font16, 'wifi', loc[0] + 8, loc[1] + 8, ili9342c.BLACK, ili9342c.GREEN)

        if btn["action"] == "TAP" or "HOLD":

            if self.m5.is_wifi_connected():
                disconnect()
            else:
                ls = scan()
                for i, l in enumerate(ls):
                    if i < count:
                        display(i, l)
                    if self.essid in l[0]:
                        connect()

    def btn_2(self, btn):
        print("Not Implemented ..")

            
    def btn_3(self, btn):
        print("Not Implemented ..")

    def btn_4(self, btn):
        if btn['action'] == 'HOLD':
            self.m5.hard_reset()

    def btn_a(self, btn):

        if btn['action'] == 'HOLD':
            self.m5.power_down()
        else:
            print("Not Implemented ..")

    def btn_b(self, btn):

        if btn['action'] == 'HOLD':
            self.m5.hard_reset()
        else:
            print("Not Implemented ..")

    def btn_c(self, btn):

        if btn['action'] == 'HOLD':
            self.m5.hard_reset()
        else:
            print("Not Implemented ..")


if __name__ == "__main__":
    """ repurposing btn_1 as wifi app btn and deleting btn_2 and btn_3"""

    try:
        wa = WifiApp(essid='TBD', pwd='????')
        wa.m5.btns['btn_1']['lbl'] = 'WiFi'
        wa.m5.btns['btn_4']['lbl'] = 'QUIT'
        wa.m5.paint_btns()

        # delete three appbtns
        v = [wa.m5.btns['btn_2'], wa.m5.btns['btn_3']]
        k = ['btn_2', 'btn_3']
        d = dict(zip(k, v))
        wa.m5.delete_btns(d)
        wa.run_apps_forever()
        
    except Exception as e:
        print(" oops I blew up ..", e)
    
    finally:
        wa.m5.hard_reset()

