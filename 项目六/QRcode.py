# Created: 20-04-2025
# by: python 3.8 and PyQt5
# coding:utf-8
# aurhor: changye❀

import sys
import qrcode
from PIL.ImageQt import ImageQt
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt


class QRCodeGenerator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # 设置窗口属性
        self.setWindowTitle('二维码生成器')
        self.setGeometry(300, 300, 400, 500)

        # 创建主部件和布局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()

        # 输入框
        self.input_label = QLabel('输入文本或URL:')
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("在此输入内容...")

        # 生成按钮
        self.generate_btn = QPushButton('生成二维码')
        self.generate_btn.clicked.connect(self.generate_qrcode)

        # 保存按钮
        self.save_btn = QPushButton('保存二维码')
        self.save_btn.clicked.connect(self.save_qrcode)
        self.save_btn.setEnabled(False)

        # 显示二维码的区域
        self.qr_label = QLabel()
        self.qr_label.setAlignment(Qt.AlignCenter)
        self.qr_label.setMinimumSize(300, 300)

        # 将部件添加到布局
        layout.addWidget(self.input_label)
        layout.addWidget(self.input_field)
        layout.addWidget(self.generate_btn)
        layout.addWidget(self.save_btn)
        layout.addWidget(self.qr_label)

        main_widget.setLayout(layout)

    def generate_qrcode(self):
        text = self.input_field.text().strip()
        if not text:
            QMessageBox.warning(self, '警告', '请输入内容！')
            return

        try:
            # 生成二维码
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(text)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")

            # 转换为QPixmap显示
            qim = ImageQt(img)
            pixmap = QPixmap.fromImage(qim)
            self.qr_label.setPixmap(pixmap)
            self.save_btn.setEnabled(True)

        except Exception as e:
            QMessageBox.critical(self, '错误', f'生成二维码失败: {str(e)}')

    def save_qrcode(self):
        if not self.qr_label.pixmap():
            return

        # 获取保存路径
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存二维码",
            "qrcode.png",
            "PNG Image (*.png);;JPEG Image (*.jpg *.jpeg)"
        )

        if file_path:
            self.qr_label.pixmap().save(file_path)
            QMessageBox.information(self, '成功', '二维码保存成功！')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = QRCodeGenerator()
    window.show()
    sys.exit(app.exec_())