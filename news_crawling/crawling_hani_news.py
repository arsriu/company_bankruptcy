from bs4 import BeautifulSoup
import requests
import pandas as pd
from tqdm.auto import tqdm
import lxml
import re
from datetime import datetime

data = pd.DataFrame(columns=['site', 'title', 'url', 'writer', 'date', 'content'])
pattern = r'\d.+'
datetime_format = "%Y-%m-%d %H:%M"


def makeUrl(keyword, page):
    url = 'https://search.hani.co.kr/search/newslist?searchword=' + keyword + '&startdate=1988.01.01&enddate=2023.11.15&page=' + str(
        page) + '&sort=desc'
    return url


def crawlingUrl(url):
    site = requests.get(url)
    site_soup = BeautifulSoup(site.text, 'lxml')
    news_list = site_soup.select('div.list')
    for news in tqdm(news_list):
        news_title = news.select('h4.article-title')[0].text
        news_title = news_title.replace('\n', '')  # 뉴스 제목
        news_url = news.find('a').get('href')  # 뉴스 url

        if news_url[8:11] == 'www':

            content_site = requests.get(news_url)
            content_soup = BeautifulSoup(content_site.text, 'lxml')

            try:
                news_writer = content_soup.find('div', {'class': 'name'}).find('strong').text  # 뉴스 기자
            except:
                news_writer = 'None'

            news_date = content_soup.find('p', {'class': 'date-time'}).find('span').text
            news_date = re.search(pattern, news_date)
            news_date = datetime.strptime(news_date.group(), datetime_format)  # 뉴스 기사 쓴 날짜

            news_content = content_soup.select('div.text')[0].text
            news_content = news_content.replace('\n', ' ')

            news_site = '한겨레'

            new_data = [news_site, news_title, news_url, news_writer, news_date, news_content]
            data.loc[len(data)] = new_data
        else:
            pass


def main():
    keyword = input('검색 키워드 : ')

    n = int(input('페이지 수 : '))

    for i in range(1, n + 1):
        url = makeUrl(keyword, i)
        crawlingUrl(url)

    # data['date'] = pd.to_datetime(data['date'], format="%Y년 %m월 %d일", errors='coerce') # 날짜를 datetime 형식으로 변환
    # data['date'] = data['date'].dt.strftime("%Y년 %m월 %d일")  # 날짜 형식을 변경
    data.to_csv(r'C:\AorF\hanitest_news.csv', encoding='utf-8-sig', index=False)

main()

