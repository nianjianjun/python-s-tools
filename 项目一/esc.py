# Created: 18-04-2025
# by: python 3.8 and PyQt5
# aurhor: changye❀
import sys
import os
from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_shut(object):
    def __init__(self):
        self.flag = True

    def setupUi(self, shut):
        shut.setObjectName("shut")
        shut.resize(420, 180)
        shut.setFixedSize(420, 180)

        self.init_widgets(shut)
        self.retranslateUi(shut)
        QtCore.QMetaObject.connectSlotsByName(shut)

    def init_widgets(self, shut):
        self.create_label(shut, "label", "在：", 40, 50)
        self.create_line_edit(shut, "lineEdit", 70, 50)
        self.create_label(shut, "label_2", "时", 150, 60)
        self.create_line_edit(shut, "lineEdit_2", 180, 50)
        self.create_label(shut, "label_3", "分", 260, 60)
        self.create_button(shut, "pushButton", "设置", 290, 50, self.sd)
        self.create_label(shut, "label_4", "    请输入关机时间", 0, 120)

    def create_label(self, parent, name, text, x, y):
        label = QtWidgets.QLabel(parent)
        label.setGeometry(QtCore.QRect(x, y, 41, 51))
        label.setFont(QtGui.QFont("Roman times", 10, QtGui.QFont.Bold))
        label.setObjectName(name)
        label.setText(text)

    def create_line_edit(self, parent, name, x, y):
        line_edit = QtWidgets.QLineEdit(parent)
        line_edit.setGeometry(QtCore.QRect(x, y, 71, 41))
        line_edit.setFont(QtGui.QFont("Roman times", 10, QtGui.QFont.Bold))
        line_edit.setObjectName(name)

    def create_button(self, parent, name, text, x, y, clicked_func):
        button = QtWidgets.QPushButton(parent, clicked=clicked_func)
        button.setGeometry(QtCore.QRect(x, y, 101, 41))
        button.setFont(QtGui.QFont("Roman times", 10, QtGui.QFont.Bold))
        button.setObjectName(name)
        button.setText(text)

    def retranslateUi(self, shut):
        pass  # 省略翻译部分

    def sd(self):
        h = self.lineEdit.text()
        m = self.lineEdit_2.text()
        if self.flag:
            self.set_shutdown(h, m)
        else:
            self.remove_shutdown()

    def set_shutdown(self, h, m):
        self.flag = False
        try:
            os.popen(f'at {h}:{m} shutdown -s')
            self.update_label(f'    设置成功! 系统将关机在今天 {h}:{m}')
            self.pushButton.setText('移除')
            self.clear_inputs()
        except:
            self.update_label('Something is wrong~')

    def remove_shutdown(self):
        self.flag = True
        try:
            os.popen('at /delete /yes')
            self.update_label('成功，全部移除')
            self.pushButton.setText('设置')
            self.clear_inputs()
        except:
            self.update_label('Something is wrong')

    def update_label(self, text):
        self.label_4.setText(text)

    def clear_inputs(self):
        self.lineEdit.clear()
        self.lineEdit_2.clear()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_shut()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())