# Created: 19-04-2025
# by: python 3.8 and PyQt5
# aurhor: changye❀
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
        self.setGeometry(100, 100, 400, 400)  # 调大窗口高度

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
                # 替换为你的实际API ID和Key
                api_id = "88888888"
                api_key = "88888888"

                # URL编码处理
                province_encoded = quote(province)
                city_encoded = quote(city)

                url = f"https://cn.apihz.cn/api/tianqi/tqyb.php?id={api_id}&key={api_key}&sheng={province_encoded}&place={city_encoded}"

                with urllib.request.urlopen(url) as response:
                    data = response.read().decode('utf-8')
                    weather_info = json.loads(data)

                if weather_info.get('code') == 200:
                    # 直接从顶层键获取数据
                    weather_info_text = (
                        f"📍 地区: {weather_info.get('place', 'N/A')}\n"
                        f"🌤️ 当前天气: {weather_info.get('weather1', 'N/A')}\n"
                        f"🌡️ 温度: {weather_info.get('temperature', 'N/A')}°C\n"
                        f"💧 湿度: {weather_info.get('humidity', 'N/A')}%\n"
                        f"🌧️ 降水量: {weather_info.get('precipitation', 'N/A')}mm\n"
                        f"🎈 气压: {weather_info.get('pressure', 'N/A')}hPa\n"
                        f"🧭 风向: {weather_info.get('windDirection', 'N/A')}\n"
                        f"🌪️ 风力等级: {weather_info.get('windScale', 'N/A')}\n"
                        f"🍃 风速: {weather_info.get('windSpeed', 'N/A')}m/s\n"
                    )
                else:
                    weather_info_text = f"❌ 错误: {weather_info.get('msg', '未知错误')}"

                self.weather_text.setText(weather_info_text)
            except urllib.error.HTTPError as e:
                self.weather_text.setText(f'HTTP错误: {e.code} {e.reason}')
            except urllib.error.URLError as e:
                self.weather_text.setText(f'网络错误: {e.reason}')
            except json.JSONDecodeError:
                self.weather_text.setText('错误: 无效的API响应格式')
            except Exception as e:
                self.weather_text.setText(f'未知错误: {str(e)}')
        else:
            self.weather_text.setText("⚠️ 请输入省份和城市名称")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = WeatherApp()
    ex.show()
    sys.exit(app.exec_())