# M5Stack Core2 firmware creation steps
A detailed procedure for compiling micropython with custom modules
Platform tested on MacOS Monterey with prerequistes as identified below

## 1. Install esp-idf
Install latest stable version of esp-idf a prerequisite to compile micro python for M5Stack Core2
Follow esp-idf installation steps with prerequisites as specified using stable version 4.4.1 
https://docs.espressif.com/projects/esp-idf/en/v4.4.1/esp32/get-started/index.html
Steps below are for MacOS Monterey

From your your home dir $HOME
@monterey ~ % mkdir -p esp
@monterey ~ % cd esp
@monterey ~/esp % git clone -b v4.4.1 --recursive https://github.com/espressif/esp-idf.git
@monterey ~/esp % cd esp-idf
@monterey ~/esp/esp-idf % ./install.sh esp32
@monterey ~/esp/esp-idf %   . ./export.sh
. # Add the following two aliases in your .zshrc profile or whatever startup shell you are using
These alias is all you need to recompile any number of times once setup correctly

alias get_idf='. $HOME/esp/esp-idf/export.sh'
alias build='make USER_C_MODULES=$HOME/esp/c_modules/ili9342c/micropython.cmake all'


## 2. Install Micropython
Install latest version of Micropython
Follow Micropython installation steps for esp32
https://github.com/micropython/micropython/tree/master/ports/esp32
Steps below are for Micropython version as of 5/9/2022

@monterey ~/esp/esp-idf % cd ..   
@monterey ~/esp % git clone --recursive https://github.com/micropython/micropython
@monterey ~/esp % cd micropython 
@monterey ~/esp/micropython %cd m	

## 3. Copy c modules
Copy c_modules folder as is from this repo at "$HOME/esp/"

## 4. Copy py modules
Copy py_modules folder "contents" at "$HOME/esp/micropython/ports/esp32/modules/"

## 5. Compile source
The detailed steps are shown below

@monterey ~ % cd $HOME/esp/micropython/ports/esp32
@monterey ~/esp/micropython/ports/esp32 % get_idf
@monterey ~/esp/micropython/ports/esp32 % build

If you made it so far you will be rewarded with the firmware file at "$HOME/esp/micropython/ports/esp32/build-GENERIC/firmware.bin"
Firmware.bin is flashed in to M5Stack Core2 hardware. There is one final step

## 6. Configure Flash Size
Change default Flash Size of 4MB to 16MB available on M5Core2 hardware
This requires manual editing of sdkconfig file created in the build process. Use of idf.py menuconfig command is another way to do
But below is faster and less frustrating as idf.py creates another build file not required.

Steps are:
Edit the esp-idf config file at $HOME/esp/micropython/ports/esp32/build-GENERIC/sdkconfig with a plain text editor
Scroll down about 20 lines  to find ..
Enable 16MB instead of default 4MB as shown below. When all changes made these lines look like  ..

. # Serial flasher config

. # CONFIG_ESPTOOLPY_FLASHSIZE_1MB is not set

. # CONFIG_ESPTOOLPY_FLASHSIZE_2MB is not set

. # CONFIG_ESPTOOLPY_FLASHSIZE_4MB is not set

. # CONFIG_ESPTOOLPY_FLASHSIZE_8MB is not set

. CONFIG_ESPTOOLPY_FLASHSIZE_16MB=y

. CONFIG_ESPTOOLPY_FLASHSIZE="16MB"

Save the file
## Recompile
Run 'build' command again
You are done!
The firmware will contain the following artifacts in a single firmware.bin file
bootloader  @0x001000    21600  (    7072 remaining)
partitions  @0x008000     3072  (    1024 remaining)
application @0x010000  1532896  (  498720 remaining)
total                  1598432

Note the 'build' command is a proxy for idf.py build ..

idf.py -D MICROPY_BOARD=GENERIC -B build-GENERIC  -DUSER_C_MODULES=/Users/bp/esp/c_modules/ili9342c/micropython.cmake build

