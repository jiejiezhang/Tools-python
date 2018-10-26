# -- coding: utf-8 -- for Chinaese comment
#上面这行可以启用中文注释

#强制使用py3格式打印函数print()
from __future__ import print_function

from ui import Ui_MainWindow
#导入PYQT5核心文件
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal,QObject
#用于字体变颜色
from PyQt5.QtGui import QPalette, QPixmap, QColor,QImage
#用于日期控件，时间处理
from PyQt5.QtCore import QDate, QTime, QDateTime, QTimer
#用于支持弹框输入
from PyQt5.QtWidgets import QLineEdit,QInputDialog,QAction,QMessageBox,QRadioButton,QFileDialog
#Qt控件
from PyQt5.QtWidgets import QStatusBar,QComboBox
#串口支持
import serial
import serial.tools.list_ports
import sys
import binascii
import struct

#mavlink操作
from pymavlink import mavutil

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        self.setWindowTitle("VID tool")
        self.setFixedSize(self.width(),self.height())

        self.statusBar=QStatusBar()
        self.setStatusBar(self.statusBar)

        self.statusBar.showMessage("python version: "+str(sys.version))
        self.button_2.clicked.connect(self.set_clicked)
        self.button_2.setEnabled(False)

        self.button_3.clicked.connect(self.read_clicked)
        self.button_3.setEnabled(False)

        self.display_label("Waitting Drone connect...（未连接）",'#FF0099')

        # timer for port state reflash.
        self.timer_getdata = QTimer(self)
        self.timer_getdata.timeout.connect(self.timer_loop)
        self.timer_getdata.start(1500)
        self.connect_state=False
        self.last_connect_state=False
        self.mavlink_is_ready=False

        self.lineEdit.textChanged.connect(self.check_input)

    def read_clicked(self):
        self.statusBar.showMessage("Reading ID.(读取中.)",2000)
        if self.mavlink_is_ready == True:
            # for py3 [str]--->(encode)--->[bytes]-->(decode)-->str
            p1 = self.read_param_retry(b'MAV_VEHICLE_ID1')
            p2 = self.read_param_retry(b'MAV_VEHICLE_ID2')
            p3 = self.read_param_retry(b'MAV_VEHICLE_ID3')
            p4 = self.read_param_retry(b'MAV_VEHICLE_ID4')

            if p1 == None or p2 == None or p3 == None or p4 == None:
                self.display_label("No vaild ID.",'#118855')
                return
            else:
                self.lineEdit.setText("READ:"+p1.decode()+p2.decode()+p3.decode()+p4.decode())
                self.lineEdit.setFocus()
                self.lineEdit.selectAll()
                self.display_label("Read ID completed. (读取ID完毕.)",'#118855')
                self.statusBar.showMessage("Done.",2000)

    def check_input(self):
        if len(self.lineEdit.text()) == 16 and self.mavlink_is_ready == True:
            if self.lineEdit.text()[:2]=="YU":
                self.button_2.setEnabled(True)
                self.statusBar.showMessage("Input vaild ID. (有效输入)",1000)
        else:
            self.button_2.setEnabled(False)

    def set_clicked(self):
        self.statusBar.showMessage("Setting... (设置中.)",2000)
        if  self.set_param_retry(b'MAV_VEHICLE_ID1',self.lineEdit.text()[0:4]) != None \
        and self.set_param_retry(b'MAV_VEHICLE_ID2',self.lineEdit.text()[4:8]) != None \
        and self.set_param_retry(b'MAV_VEHICLE_ID3',self.lineEdit.text()[8:12]) != None \
        and self.set_param_retry(b'MAV_VEHICLE_ID4',self.lineEdit.text()[12:16]) != None :
            self.display_label("**Set ID successful** ( 设置ID成功 ）",'#118855')
            self.statusBar.showMessage("Done. (设置完毕)",3000)
            # Empty text content for factory to prevent fools
            self.lineEdit.setText('')
            return
        self.display_label("**Set ID Fail** (设置失败）",'#FF0000')
        self.statusBar.showMessage("Set ID Error. (错误)",2000)
        self.lineEdit.setText('')

    def read_param_retry(self,param_name='None',timeout_s=1,retry=3):
        for t in range(retry):
            try:
                self.mav.mav.param_request_read_send(self.mav.target_system, self.mav.target_component,param_name,-1)
                message = self.mav.recv_match(type='PARAM_VALUE', blocking=True, timeout=timeout_s)
            except:
                message = None
            if message != None :
                message=message.to_dict()
                if str_to_bytes(message['param_id']) == param_name:
                    print("get %s = %s"%(message['param_id'], struct.pack('f', message['param_value']).decode() ))
                    return struct.pack('f', message['param_value'])
        return None

    def set_param_retry(self,param_name='None',value=b'None',timeout_s=1,retry=3):
        value_f, = struct.unpack('1f',str_to_bytes(value))
        for t in range(retry):
            try:
                self.mav.mav.param_set_send(self.mav.target_system, self.mav.target_component,param_name,value_f,mavutil.mavlink.MAV_PARAM_TYPE_INT32)
                message = self.mav.recv_match(type='PARAM_VALUE', blocking=True, timeout=timeout_s)
            except:
                message = None
            if message != None :
                message=message.to_dict()
                if str_to_bytes(message['param_id']) == param_name and message['param_value']==value_f:
                    print("Set %s to %s"%(message['param_id'], struct.pack('f', message['param_value']).decode() ))
                    return True
                else:
                    #print bad info.
                    print(message['param_id'])
                    print(param_name)
                    print(value_f)
                    print(message['param_value'])
        return None

    def Wait_HEARTBEAT(self,timeout_s=1,retry=2):
        for t in range(retry):
            try:
                message = self.mav.recv_match(type='HEARTBEAT', blocking=True, timeout=timeout_s)
            except:
                pass
            if message != None:
                return True
        return None

    def timer_loop(self):
        self.port_name=''
        port_list = list(serial.tools.list_ports.comports())
        # ST VCP usb device vid is 0x26AC. looking for it.
        for port in port_list:
            if port.vid == 0x26AC:
                self.port_name=str(port).split()[0]

        #found ST VCP usb device.
        if self.port_name != '' :
            self.connect_state=True
        else:
            self.connect_state=False
            self.button_3.setEnabled(False)
            self.button_2.setEnabled(False)
            self.mavlink_is_ready = False

        try:
            #if state changed make a mavlink obj or close it.
            if self.last_connect_state != self.connect_state:
                if self.connect_state == True:
                    print("Found device : %s, Creat mavutil."%self.port_name)
                    self.statusBar.showMessage("Found device waiting mavlink.",1000)
                    self.mav = mavutil.mavlink_connection(self.port_name, baud=57600)
                    #message = self.mav.recv_match(type='HEARTBEAT', blocking=True, timeout=4)
                    if self.Wait_HEARTBEAT() != None :
                        self.mavlink_is_ready=True
                        print("Drone Connected. HEARTBEAT received.")
                        self.display_label("Drone Connected. HEARTBEAT received. （飞机连接成功）",'#118855')
                        # set Focus to lineEdit.
                        self.check_input()
                        self.lineEdit.setFocus()
                        self.lineEdit.selectAll()
                        self.button_3.setEnabled(True)
                    else:
                        # FC did not send mavlink. maybe stuck at bootloader.
                        self.mav.close()
                        self.display_label("No respond.Please try reboot.（无响应，重启飞机后插入）",'#FF0000')
                        self.last_connect_state = self.connect_state = False
                        return
                else:
                    print("close mavutil")
                    self.mav.close()
                    self.display_label("Waitting Drone connect...（未连接）",'#FF0000')
                    self.lineEdit.setText("")
                    self.mavlink_is_ready=False
        except:
            print("port operation fail.port unstable.(连接不稳定)")
            self.statusBar.showMessage("port operation fail.port unstable.(连接不稳定)",2000)
            self.last_connect_state = False
            # Even connection still disbale. Once try mavlink_connection() should use close(). 
            self.mav.close()
            return

        self.last_connect_state=self.connect_state

    #设置显示label
    def display_label(self,text,color):
            self.label.setText(text)
            self.label.setVisible(True)
            background_color = QColor()
            background_color.setNamedColor(color)
            pe = QPalette()
            pe.setColor(QPalette.WindowText,background_color)
            self.label.setPalette(pe)


def str_to_bytes(str):
    if sys.version_info.major == 2:
        return bytes(str)
    return bytes(str,encoding='utf-8')

#Main函数，生成主窗口
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())

