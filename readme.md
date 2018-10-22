
## This is a tool for display serial data to your screen.

Feture:
1. Automatic connect to serial port.
2. param setting.
3. param read back.

Build tool :

0. python 2.7/3.5
1. PyQT5
2. pyinstaller (optional)
3. Qt Qtdesigner (optional)

### How to install them:

1. install qt5
`sudo apt-get install qt5-default qttools5-dev-tools`

2. install pyqt5
`sudo apt-get install python3-pyqt5 pyqt5-dev-tools`

3. install executable package tools.(optional,If you no need to package it to a executable program.)

Note:for package pvmavlink pyinstaller should base on python3.5. python2.7 will have a issue.
pip3 install pyinstaller

### How to Modify / update GUI design:

step 1. Run Qtdesigner with "designer" command. Open UI design file "ui.ui".

step 2. Modify UI. Then save it.

step 3. run command: `pyuic5 -o ui.py ui.ui` . You will get python file "ui.py" , Done.

### How to run:
Run:python ComHelper.py

### How to release a executable program:

Note: for package pymavlink on Windows, should add :

```
hiddenimports=['pymavlink.dialects.v20','pymavlink.dialects.v20.ardupilotmega',]
```
to spec file.

Linux\Mac Run: `pyinstaller -F --clean vid_tool.spec`
Windows Run: `pyinstaller -F --clean -w vid_tool.spec`

You will get a executable file at "./dist".

#### Addtion note :

1. Fix `Can't open /dev/ttyACM0 permission denide.`
Run: `sudo usermod -a -G dialout <Your_user_name>`
