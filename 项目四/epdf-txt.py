# Created: 20-04-2025
# by: python 3.8 and PyQt5
# coding:utf-8
# aurhor: changye❀
# coding: utf-8
import sys
import os
import re
import hashlib
import random
import requests
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QFileDialog,
                             QProgressBar, QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from pdfminer.high_level import extract_text
import time


class TranslationWorker(QThread):
    progress_updated = pyqtSignal(int, str)
    finished = pyqtSignal(str)

    def __init__(self, pdf_path, appid, secret_key):
        super().__init__()
        self.pdf_path = pdf_path
        self.appid = appid
        self.secret_key = secret_key
        self.output_path = os.path.splitext(pdf_path)[0] + "_双语对照.txt"
        self.max_bytes = 2000 * 3  # 2000个汉字（UTF-8占3字节）
        self.running = True

    def run(self):
        try:
            # 1. 提取并预处理文本
            raw_text = self.preprocess_text(extract_text(self.pdf_path))

            # 2. 智能分段
            paragraphs = self.intelligent_segment(raw_text)

            # 3. 批量翻译
            self.batch_translate(paragraphs)

            self.finished.emit(self.output_path)

        except Exception as e:
            self.finished.emit(f"错误: {str(e)}")

    def preprocess_text(self, text):
        """文本预处理"""
        # 合并换行符
        text = re.sub(r'-\n+', '', text)  # 处理换行连字符
        text = re.sub(r'\n+', '\n', text)  # 合并多个换行
        # 标准化Unicode
        return text.encode('utf-8', 'ignore').decode('utf-8')

    def intelligent_segment(self, text):
        """智能分段算法"""
        segments = []
        current_segment = []
        current_length = 0

        # 按自然段落分割
        for paragraph in filter(None, text.split('\n')):
            para_bytes = len(paragraph.encode('utf-8'))

            # 段落短于限制直接添加
            if current_length + para_bytes <= self.max_bytes:
                current_segment.append(paragraph)
                current_length += para_bytes
            else:
                # 长段落二次分割
                if current_segment:
                    segments.append('\n'.join(current_segment))
                    current_segment = []
                    current_length = 0

                # 按句子分割长段落
                sentences = re.split(r'(?<=[。！？.?!])', paragraph)
                for sentence in sentences:
                    sent_bytes = len(sentence.encode('utf-8'))
                    if sent_bytes > self.max_bytes:
                        # 处理超长句子
                        chunks = self.split_by_bytes(sentence, self.max_bytes)
                        segments.extend(chunks)
                    elif current_length + sent_bytes > self.max_bytes:
                        segments.append('\n'.join(current_segment))
                        current_segment = [sentence]
                        current_length = sent_bytes
                    else:
                        current_segment.append(sentence)
                        current_length += sent_bytes

        if current_segment:
            segments.append('\n'.join(current_segment))

        return segments

    def split_by_bytes(self, text, max_bytes):
        """按字节数精确分割"""
        chunks = []
        current_chunk = []
        current_len = 0

        for char in text:
            char_len = len(char.encode('utf-8'))
            if current_len + char_len > max_bytes:
                chunks.append(''.join(current_chunk))
                current_chunk = [char]
                current_len = char_len
            else:
                current_chunk.append(char)
                current_len += char_len

        if current_chunk:
            chunks.append(''.join(current_chunk))

        return chunks

    def batch_translate(self, paragraphs):
        """批量翻译处理"""
        total = len(paragraphs)
        success_count = 0

        with open(self.output_path, 'w', encoding='utf-8') as f:
            for idx, para in enumerate(paragraphs, 1):
                if not self.running:
                    break

                # 翻译重试机制
                for attempt in range(3):
                    try:
                        translated = self.translate_paragraph(para)
                        f.write(f"【原文 {idx}】\n{para}\n")
                        f.write(f"【译文 {idx}】\n{translated}\n\n")
                        success_count += 1
                        status = f"成功翻译段落 {idx}/{total}"
                        self.progress_updated.emit(int(idx / total * 100), status)
                        break
                    except Exception as e:
                        if attempt == 2:
                            self.progress_updated.emit(
                                int(idx / total * 100),
                                f"段落 {idx} 失败: {str(e)}"
                            )
                            f.write(f"【原文 {idx}】\n{para}\n【翻译失败】\n\n")
                        time.sleep(2 ** attempt)  # 指数退避
                else:
                    continue

                # QPS控制
                time.sleep(1.2)  # 确保符合1次/秒的限制

        # 生成质量报告
        report = f"\n翻译完成率: {success_count}/{total} ({success_count / total:.1%})"
        with open(self.output_path, 'a') as f:
            f.write(report)

    def translate_paragraph(self, text):
        """执行单段落翻译（已修复参数顺序问题）"""
        # 生成随机盐值
        salt = random.randint(10000, 99999)

        # 计算签名
        sign_str = f"{self.appid}{text}{salt}{self.secret_key}"
        sign = hashlib.md5(sign_str.encode()).hexdigest()

        # 构建请求参数
        params = {
            'q': text,
            'from': 'auto',
            'to': 'zh',
            'appid': self.appid,
            'salt': salt,
            'sign': sign
        }

        try:
            response = requests.get(
                "http://api.fanyi.baidu.com/api/trans/vip/translate",
                params=params,
                timeout=15
            )
            response.raise_for_status()

            data = response.json()
            if 'error_code' in data:
                raise Exception(f"{data['error_msg']} (代码 {data['error_code']})")

            return ' '.join([res['dst'] for res in data['trans_result']])

        except requests.exceptions.RequestException as e:
            raise Exception(f"网络请求失败: {str(e)}")
        except KeyError:
            raise Exception("API响应格式异常")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.worker = None
        self.config = {
            'appid': '20250420002337893',  # 替换为你的APPID
            'secret_key': 'XDAEQWe319Di7PnVnQw6'  # 替换为你的密钥
        }

    def setup_ui(self):
        self.setWindowTitle("智能PDF翻译工具")
        self.setGeometry(300, 300, 600, 150)

        main_widget = QWidget()
        layout = QVBoxLayout()

        # 文件选择
        file_layout = QHBoxLayout()
        self.btn_file = QPushButton("选择PDF文件")
        self.btn_file.clicked.connect(self.choose_file)
        self.lbl_file = QLabel("未选择文件")
        file_layout.addWidget(self.btn_file)
        file_layout.addWidget(self.lbl_file)

        # 进度显示
        self.progress = QProgressBar()
        self.lbl_status = QLabel("就绪")

        # 控制按钮
        self.btn_start = QPushButton("开始翻译")
        self.btn_start.clicked.connect(self.toggle_translation)
        self.btn_stop = QPushButton("停止")
        self.btn_stop.clicked.connect(self.stop_translation)
        self.btn_stop.setEnabled(False)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.btn_start)
        button_layout.addWidget(self.btn_stop)

        layout.addLayout(file_layout)
        layout.addWidget(self.progress)
        layout.addWidget(self.lbl_status)
        layout.addLayout(button_layout)

        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

    def choose_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择PDF文件", "", "PDF文件 (*.pdf)")
        if path:
            self.lbl_file.setText(path)
            self.btn_start.setEnabled(True)

    def toggle_translation(self):
        if self.worker and self.worker.isRunning():
            return

        pdf_path = self.lbl_file.text()
        if not os.path.exists(pdf_path):
            QMessageBox.critical(self, "错误", "请选择有效的PDF文件")
            return

        self.worker = TranslationWorker(pdf_path, **self.config)
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.finished.connect(self.on_finished)

        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.worker.start()

    def stop_translation(self):
        if self.worker and self.worker.isRunning():
            self.worker.running = False
            self.worker.terminate()
            self.btn_start.setEnabled(True)
            self.btn_stop.setEnabled(False)
            QMessageBox.information(self, "已停止", "翻译任务已中止")

    def update_progress(self, percent, status):
        self.progress.setValue(percent)
        self.lbl_status.setText(status)

    def on_finished(self, result):
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)

        if result.startswith("错误:"):
            QMessageBox.critical(self, "错误", result[3:])
        else:
            QMessageBox.information(self, "完成",
                                    f"翻译文件已保存至:\n{result}\n\n将自动打开所在文件夹")
            self.open_folder(os.path.dirname(result))

    def open_folder(self, path):
        if sys.platform == 'win32':
            os.startfile(path)
        elif sys.platform == 'darwin':
            os.system(f'open "{path}"')
        else:
            os.system(f'xdg-open "{path}"')

    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            self.stop_translation()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())