
# This is a tool for display serial data to your screen.

Feture:
1. Automatic serial port scaning.
2. Wide rang baudrate setting.
3. Ascii and Hex format support.
4. Text string sending support.

Build tool :

0. python 2.7/3.5
1. PyQT5
2. pyinstaller (optional)
3. Qt Qtdesigner (optional)

# How to install them:

1. install qt5
sudo apt-get install qt5-default qttools5-dev-tools

2. install pyqt5
sudo apt-get install python3-pyqt5 pyqt5-dev-tools

3. install executable package tools.(optional,If you no need to package it to a executable program.)
pip3 install pyinstaller

# How to Modify / update GUI design:

step 1. Run Qtdesigner with "designer" command. Open UI design file "ui.ui".

step 2. Modify UI. Then save it.

step 3. run command: "pyuic5 -o ui.py ui.ui" . You will get python file "ui.py" , Done.

# How to run:
Run:python ComHelper.py

# How to release a executable program:
Run:pyinstaller -F ComHelper.py -p ui.py

You will get a executable file at "./dist".