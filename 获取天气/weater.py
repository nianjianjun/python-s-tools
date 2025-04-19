import sys
import urllib.request
import json
from urllib.parse import quote
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit


class WeatherApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("天气信息获取")
        self.setGeometry(100, 100, 400, 300)

        self.layout = QVBoxLayout()

        self.province_label = QLabel("省份:", self)
        self.layout.addWidget(self.province_label)

        self.province_input = QLineEdit(self)
        self.layout.addWidget(self.province_input)

        self.city_label = QLabel("城市:", self)
        self.layout.addWidget(self.city_label)

        self.city_input = QLineEdit(self)
        self.layout.addWidget(self.city_input)

        self.get_weather_button = QPushButton("获取天气信息", self)
        self.get_weather_button.clicked.connect(self.get_weather)
        self.layout.addWidget(self.get_weather_button)

        self.weather_text = QTextEdit(self)
        self.weather_text.setReadOnly(True)
        self.layout.addWidget(self.weather_text)

        self.setLayout(self.layout)

    def get_weather(self):
        province = self.province_input.text().strip()
        city = self.city_input.text().strip()
        if province and city:
            try:
                api_id = "88888888"  # 替换为实际API ID
                api_key = "88888888"  # 替换为实际API Key
                # URL编码省份和城市名称
                province_encoded = quote(province)
                city_encoded = quote(city)
                url = f"https://cn.apihz.cn/api/tianqi/tqyb.php?id={api_id}&key={api_key}&sheng={province_encoded}&place={city_encoded}"

                with urllib.request.urlopen(url) as response:
                    data = response.read().decode('utf-8')
                    weather_info = json.loads(data)

                if weather_info.get('code') == 200:
                    # 假设数据在'data'字段内
                    data = weather_info.get('data', {})
                    weather_info_text = (
                        f"省份: {data.get('sheng', province)}\n"
                        f"城市: {data.get('place', city)}\n"
                        f"天气: {data.get('tianqi', 'N/A')}\n"
                        f"温度: {data.get('wendu', 'N/A')}°C\n"
                        f"湿度: {data.get('shidu', 'N/A')}%\n"
                        f"风向: {data.get('fengxiang', 'N/A')}\n"
                        f"风力: {data.get('fengli', 'N/A')}\n"
                    )
                else:
                    weather_info_text = f"错误: {weather_info.get('msg', '未知错误')}"

                self.weather_text.setText(weather_info_text)
            except urllib.error.HTTPError as e:
                self.weather_text.setText(f'HTTP错误: {e.code} {e.reason}')
            except urllib.error.URLError as e:
                self.weather_text.setText(f'网络错误: {e.reason}')
            except json.JSONDecodeError:
                self.weather_text.setText('解析响应失败，请检查API返回数据')
            except Exception as e:
                self.weather_text.setText(f'发生错误: {str(e)}')
        else:
            self.weather_text.setText("请输入省份和城市名称")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = WeatherApp()
    ex.show()
    sys.exit(app.exec_())