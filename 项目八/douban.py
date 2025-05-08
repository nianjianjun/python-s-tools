import requests
from bs4 import BeautifulSoup
import csv
import time
import random
import os

# 基础配置
BASE_URL = "https://movie.douban.com/top250"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Referer": "https://movie.douban.com/"
}


def get_page(url):
    """发送HTTP请求获取页面内容（增加重试机制）"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.encoding = 'utf-8'
        if response.status_code == 200:
            return response.text
        print(f"请求失败，状态码：{response.status_code}")
        return None
    except Exception as e:
        print(f"请求异常：{str(e)}")
        return None


def parse_html(html):
    """解析HTML提取数据（增强容错）"""
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', class_='item')

    data = []
    for item in items:
        # 电影标题（处理多标题情况）
        title_elem = item.find('span', class_='title')
        title = title_elem.text.strip() if title_elem else "未知标题"

        # 评分
        rating_elem = item.find('span', class_='rating_num')
        rating = rating_elem.text.strip() if rating_elem else "无评分"

        # 简介
        quote_elem = item.find('span', class_='inq')
        quote = quote_elem.text.strip() if quote_elem else ""

        # 其他信息
        info_elem = item.find('div', class_='bd').find('p')
        if info_elem:
            info_text = info_elem.get_text(strip=True, separator='\n')
            info = info_text.split('\n')[-1].strip()
        else:
            info = "无信息"

        data.append({
            'title': title,
            'rating': rating,
            'quote': quote,
            'info': info
        })
    return data


def save_to_csv(data, filename='douban_top250.csv'):
    """保存数据到CSV文件（增加路径提示）"""
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=['title', 'rating', 'quote', 'info'])
        writer.writeheader()
        writer.writerows(data)
        f.flush()
    print(f"文件已保存到：{os.path.abspath(filename)}")


def main():
    all_data = []
    for page in range(0, 250, 25):
        url = f"{BASE_URL}?start={page}"
        print(f"正在爬取：{url}")
        html = get_page(url)
        if html:
            page_data = parse_html(html)
            all_data.extend(page_data)
            print(f"已爬取第{page // 25 + 1}页数据，获得{len(page_data)}条记录")
        else:
            print(f"第{page // 25 + 1}页爬取失败")
        time.sleep(random.uniform(1, 3))  # 随机延时更自然

    if all_data:
        save_to_csv(all_data)
    else:
        print("未获取到任何数据，请检查网络和反爬策略")


if __name__ == "__main__":
    main()