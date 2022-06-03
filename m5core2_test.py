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
from m5core2_p import M5core2


class M5core2Test:
    """ an attempt to test all methods in m5core2.py """

    def __init__(self, essid=None, pwd=None, mdir='/sd', imu_samples=10, imu_wait=100, btntest=10):

        self.mdir = mdir
        self.imu_samples = imu_samples
        self.imu_wait = imu_wait
        self.btntest = btntest

        self.m5 = M5core2(essid, pwd, mdir=self.mdir, imu_samples=self.imu_samples,
                          imu_wait=self.imu_wait)

    def btn_gesture_test(self):      
        """ test method: touch.btn_gesture() """
        
        touchctr = 4
        print("btn_gesture test runs for {} iterations ..\n"
              "on configured btns TAP, HOLD or swipe LEFT, RIGHT, UP or DOWN ..".format(touchctr))

        for i in range(touchctr):
            print(i + 1, end='')
            while self.m5.touch.btn_gesture() is None:
                pass
        print("exiting btn_gesture_test ..")

    def add_delete_btn_test(self):

        # delete three appbtns and run gesture test
        self.m5.delete_btn('btn_1', M5core2.btn_1)
        self.m5.delete_btn('btn_2', M5core2.btn_2)
        self.m5.delete_btn('btn_3', M5core2.btn_3)
        self.btn_gesture_test()

        # repurpose space released by btn_ and btn_2, relabel btn_4 and run gesture test
        self.m5.add_btn('btn_12', {'loc': (0, 208, 158, 32), 'lbl': 'JoinBtn12'})

        self.m5.btn['btn_4']['lbl'] = 'Exit'
        self.btn_gesture_test()

    def wifi_test(self):

        if not self.m5.is_wifi_connected():
            self.m5.connect_wifi()
        else:
            print("wifi is already connected ..")
        self.m5.scan_wifi()
        self.m5.disconnect_wifi()

    def imu_test(self):

        print("read_imu() returns IMU ID, 3-axis linear accl, 3-axis angular accl, timestamp and IMU temp  ..")
        [print("  {} -> {}".format(item[0], item[1:][0])) for item in self.m5.read_imu().items()]

    def hall_test(self):

        print("read_hall_sensor ..")
        [print("  {} -> {} {}".format(item[0], item[1][0], item[1][1])) for item in self.m5.read_hall_sensor().items()]

    def cpu_temp_test(self):

        print("read_raw_temp -> {}".format(self.m5.read_raw_temp()))

    def imu_scan_test(self):

        print("save_imu for {} samples at {} ms intervals -> ..".format(self.m5.imu_samples, self.m5.imu_wait))
        self.m5.save_imu_scan()

    def sdcard_erase_test(self):

        self.m5.mount_sd()
        f = 'lib'
        print("trying to erase {} if exits ..".format(f))
        self.m5.erase_sd(f)
        self.m5.release_spi2()

    def soft_reset_test(self):
        """ perform soft reset """

        self.m5.soft_reset()

    def hard_reset_test(self):
        """ perform hard reset """

        self.m5.hard_reset()

    def write_test(self):
        """ test writing-in and erasing the window area """
        
        self.m5.write(tl=["This is a test for many ", "text", "chunks"], xl=[0, 176, 224], yl=[48, 64, 80])

    def update_clock_test(self):

        self.m5.update_clock()

    def powerdown_test(self):

        self.m5.power_down()


if __name__ == "__main__":
    """ execute various methods sequentially """

    m5t = M5core2Test(essid='TBD', pwd='????')
    
    tests = ["btn_gesture_test",
             "add_delete_btn_test",
             "wifi_test",
             "imu_test",
             "hall_test",
             "cpu_temp_test",
             "imu_scan_test",
             "sdcard_erase_test",
             "write_test",
             "update_clock_test",
             "hard_reset_test"]
    try:
        for test in tests:
            print("\n    ********** {} **********".format(test))
            func = getattr(m5t, test)
            func()
            print("'{}' completed successfully ..".format(test))
    except Exception as e:
        print(" oops I blew up ..", e)
        m5t.m5.hard_reset()
