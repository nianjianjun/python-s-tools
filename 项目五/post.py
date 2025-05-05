# Created: 19-04-2025
# by: python 3.8 and psycopg2-binary
# author: changye❀
# PyQt5 版本：5.15.4

import sys
import psycopg2
import logging
from psycopg2 import sql, errors
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox, QFormLayout
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

# ------------------------- 转账核心逻辑 -------------------------
class TransferMoney:
    def __init__(self, conn):
        self.conn = conn

    def check_acct_available(self, acctid):
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = sql.SQL("SELECT acctid FROM account WHERE acctid = %s")
            cursor.execute(query, (acctid,))
            if not cursor.fetchone():
                raise Exception(f"账户 {acctid} 不存在")
        finally:
            if cursor:
                cursor.close()

    def has_enough_money(self, acctid, money):
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = sql.SQL("""
                SELECT money FROM account 
                WHERE acctid = %s AND money >= %s 
                FOR UPDATE
            """)
            cursor.execute(query, (acctid, money))
            if not cursor.fetchone():
                raise Exception(f"账户 {acctid} 余额不足")
        finally:
            if cursor:
                cursor.close()

    def reduce_money(self, acctid, money):
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = sql.SQL("""
                UPDATE account 
                SET money = money - %s 
                WHERE acctid = %s
            """)
            cursor.execute(query, (money, acctid))
            if cursor.rowcount != 1:
                raise Exception(f"账户 {acctid} 扣款失败")
        finally:
            if cursor:
                cursor.close()

    def add_money(self, acctid, money):
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = sql.SQL("""
                UPDATE account 
                SET money = money + %s 
                WHERE acctid = %s
            """)
            cursor.execute(query, (money, acctid))
            if cursor.rowcount != 1:
                raise Exception(f"账户 {acctid} 加款失败")
        finally:
            if cursor:
                cursor.close()

    def transfer(self, source_acctid, target_acctid, money):
        try:
            original_autocommit = self.conn.autocommit
            self.conn.autocommit = False  # 关闭自动提交

            self.check_acct_available(source_acctid)
            self.check_acct_available(target_acctid)
            self.has_enough_money(source_acctid, money)
            self.reduce_money(source_acctid, money)
            self.add_money(target_acctid, money)

            self.conn.commit()  # 显式提交事务

        except Exception as e:
            self.conn.rollback()  # 回滚事务
            raise e
        finally:
            self.conn.autocommit = original_autocommit

# ------------------------- GUI 界面部分 -------------------------
class TransferThread(QThread):
    result_signal = pyqtSignal(bool, str)

    def __init__(self, source, target, amount):
        super().__init__()
        self.source = source
        self.target = target
        self.amount = amount

    def run(self):
        conn = None
        try:
            # 创建独立连接（确保使用正确凭据）
            conn = psycopg2.connect(
                host="localhost",
                user="postgres",    # 确保用户名正确
                password="123456",
                dbname="postgres",
                port=5432
            )
            tr = TransferMoney(conn)
            tr.transfer(self.source, self.target, self.amount)
            self.result_signal.emit(True, "转账成功")
        except Exception as e:
            self.result_signal.emit(False, str(e))
        finally:
            if conn:
                conn.close()

class BankTransferApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("银行转账系统")
        self.setGeometry(300, 300, 400, 250)
        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        main_widget.setLayout(layout)

        # 输入表单
        form = QFormLayout()
        self.source_input = QLineEdit()
        self.target_input = QLineEdit()
        self.amount_input = QLineEdit()

        form.addRow("转出账户:", self.source_input)
        form.addRow("转入账户:", self.target_input)
        form.addRow("金额:", self.amount_input)
        layout.addLayout(form)

        # 转账按钮
        self.transfer_btn = QPushButton("执行转账")
        self.transfer_btn.clicked.connect(self.start_transfer)
        layout.addWidget(self.transfer_btn)

        # 状态显示
        self.status_label = QLabel("就绪")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        # 初始化日志
        logging.basicConfig(level=logging.DEBUG)

    def start_transfer(self):
        source = self.source_input.text().strip()
        target = self.target_input.text().strip()
        amount = self.amount_input.text().strip()

        # 输入验证
        if not all([source, target, amount]):
            QMessageBox.warning(self, "输入错误", "所有字段必须填写")
            return

        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "输入错误", "金额必须为有效正数")
            return

        # 禁用按钮防止重复提交
        self.transfer_btn.setEnabled(False)
        self.status_label.setText("处理中...")
        self.status_label.setStyleSheet("color: blue")

        # 启动线程
        self.thread = TransferThread(source, target, amount)
        self.thread.result_signal.connect(self.handle_result)
        self.thread.start()

    def handle_result(self, success, message):
        self.transfer_btn.setEnabled(True)
        if success:
            self.status_label.setStyleSheet("color: green")
            QMessageBox.information(self, "成功", message)
            self.clear_inputs()
        else:
            self.status_label.setStyleSheet("color: red")
            self.show_error_dialog(message)
        self.status_label.setText(message)

    def clear_inputs(self):
        self.source_input.clear()
        self.target_input.clear()
        self.amount_input.clear()

    def show_error_dialog(self, message):
        error_type = "数据库错误" if "psycopg2" in message else "业务错误"
        QMessageBox.critical(self, error_type, message)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BankTransferApp()
    window.show()
    sys.exit(app.exec_())