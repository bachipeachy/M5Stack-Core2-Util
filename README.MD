# M5Core2 App Development Utilities
A python utility for developing apps for M5Stack Core2 hardware


## Scope
* m5core2.py contains a python class with various methods to simplify M5core2 apps using the touch screen, SDCard and various embedded IOT sensors.
* These sensors include 6-axis IMU (Inertial Measuring Unit), Hall effect magfield sensor, temperature sensors and wireless devices.
* The utility for Bluetooth to be added later.
* A test script is added to exercise various methods

## Installation
* Flash the hardware with custom firmare "firmware.bin"
* With formatted SDCard inserted, run the script m5core2_test.py
* As a more custom option, the firmware can be produced from source. Detailed procedure is documented in file "m5core2_firmware_creation_steps.MD"
* The custom firmware freezes C module for TFT (LCD) and Python modules for AXP Power system, SDCard, Touchscreen, IMU and Hall Sensor.
* The Micropython stock drivers for SDCard and Touchscreen are replaced by enhanced SDCard and FocalTouch drivers. You can get a list of modules by running help('modules') in REPL commandline

## wifI_app
* Sample app that uses many of the utilities provided by M5core2 class

## Note
* The last update in its curent configuration has been made with this release
* The project will tranform in to a new refactored code -- stay tuned
* The plan is to create a BtnOS (acronym for Button Operating System) -- prounced as ButtonOS 