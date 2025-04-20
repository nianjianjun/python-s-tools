# -*- coding:utf-8 -*-

import sys
import random
import hashlib
import requests
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, QTextEdit

def getTransText(in_text):
    q = in_text
    fromLang = 'auto'  # 翻译源语言=自动检测
    toLang1 = 'auto'  # 译文语言 = 自动检测

    appid = '20250420002337893'
    salt = random.randint(32768, 65536)
    secretKey = 'XDAEQWe319Di7PnVnQw6'  # 密钥


    # 生成sign
    sign = appid + q + str(salt) + secretKey
    # 计算签名sign(对字符串1做md5加密，注意计算md5之前，串1必须为UTF-8编码)
    m1 = hashlib.md5(sign.encode('utf-8'))
    sign = m1.hexdigest()

    # 计算完整请求
    myurl = '/api/trans/vip/translate'
    myurl = myurl + '?appid=' + appid + '&q=' + q + '&from=' + fromLang + '&to=' + toLang1 + '&salt=' + str(
        salt) + '&sign=' + sign
    url = "http://api.fanyi.baidu.com" + myurl

    # 发送请求
    url = url.encode('utf-8')
    res = requests.get(url)

    # 转换为字典类型
    res = eval(res.text)
    return (res["trans_result"][0]['dst'])

class TranslatorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('翻译工具')
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()

        self.input_text = QLineEdit(self)
        self.input_text.setPlaceholderText('输入要翻译的文本')
        self.input_text.setFixedHeight(50)  # 设置固定高度
        layout.addWidget(self.input_text)

        self.translate_button = QPushButton('翻译', self)
        self.translate_button.clicked.connect(self.translate)
        layout.addWidget(self.translate_button)

        self.output_text = QTextEdit(self)
        self.output_text.setPlaceholderText('翻译结果')
        layout.addWidget(self.output_text)

        self.setLayout(layout)

    def translate(self):
        in_text = self.input_text.text()
        result = getTransText(in_text)
        self.output_text.setText(result)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = TranslatorApp()
    ex.show()
    sys.exit(app.exec_())
