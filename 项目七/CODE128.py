# Created: 07-05-2025
# by: python 3.8 and PyQt5 and code128
# coding:utf-8
# aurhor: changye❀

import sys
from barcode import Code128
from barcode.writer import ImageWriter
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
from io import BytesIO


class BarcodeGenerator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.barcode_image = None  # 存储生成的条码图像

    def initUI(self):
        self.setWindowTitle('CODE128条码生成器')
        self.setGeometry(300, 300, 600, 400)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()

        # 输入组件
        self.input_label = QLabel('输入内容（支持ASCII 0-127）：')
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("请输入文本或数字...")

        # 按钮
        self.generate_btn = QPushButton('生成条码')
        self.generate_btn.clicked.connect(self.generate_barcode)

        self.save_btn = QPushButton('保存条码')
        self.save_btn.clicked.connect(self.save_barcode)
        self.save_btn.setEnabled(False)

        # 显示区域
        self.barcode_label = QLabel()
        self.barcode_label.setAlignment(Qt.AlignCenter)
        self.barcode_label.setMinimumSize(400, 200)

        # 布局
        layout.addWidget(self.input_label)
        layout.addWidget(self.input_field)
        layout.addWidget(self.generate_btn)
        layout.addWidget(self.save_btn)
        layout.addWidget(self.barcode_label)

        main_widget.setLayout(layout)

    def generate_barcode(self):
        text = self.input_field.text().strip()
        if not text:
            QMessageBox.warning(self, '警告', '请输入内容！')
            return

        try:
            # 生成CODE128条码
            barcode_buffer = BytesIO()
            code128 = Code128(text, writer=ImageWriter())
            code128.write(barcode_buffer, options={
                'module_width': 0.3,  # 条码宽度
                'module_height': 15,  # 条码高度
                'font_size': 5,  # 底部文字大小
                'text_distance': 2,  # 文字与条码距离
                'quiet_zone': 5  # 左右空白区
            })

            # 转换为QPixmap
            qimg = QImage()
            qimg.loadFromData(barcode_buffer.getvalue())
            pixmap = QPixmap.fromImage(qimg)

            # 等比例缩放显示
            self.barcode_label.setPixmap(pixmap.scaledToWidth(400))
            self.save_btn.setEnabled(True)

        except Exception as e:
            QMessageBox.critical(self, '错误', f'生成失败: {str(e)}')

    def save_barcode(self):
        if not self.barcode_label.pixmap():
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存条码",
            "barcode.png",
            "PNG Image (*.png);;JPEG Image (*.jpg *.jpeg)"
        )

        if file_path:
            self.barcode_label.pixmap().save(file_path)
            QMessageBox.information(self, '成功', '条码保存成功！')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BarcodeGenerator()
    window.show()
    sys.exit(app.exec_())