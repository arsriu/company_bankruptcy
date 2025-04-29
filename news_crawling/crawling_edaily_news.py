# 날짜로 크롤링 해오기 실행 되는거
from bs4 import BeautifulSoup
import requests
import pandas as pd
from tqdm.auto import tqdm
import re
from datetime import datetime
import bul

# 날짜 정규표현식
data = pd.DataFrame(columns=['site', 'title', 'url', 'writer', 'date', 'content', 'bul'])
pattern = r'(\d{4}.\d{2}.\d{2})'


def makeUrl(keyword, n):  # 입력한 페이지의 url을 변환하는 함수
    url = 'https://www.edaily.co.kr/search/news/?keyword=' + keyword + '&page= ' + str(n)
    return url


def crawlingSite(url):
    content_site = requests.get(url)
    content_soup = BeautifulSoup(content_site.text, 'lxml')
    content = content_soup.select('div.news_body')[0].text
    text_without_spaces = "".join(content.split())
    news_content = text_without_spaces

    bul.content = news_content
    keyword_txt = bul.main()

    return keyword_txt


def crawlingUrl(url):  # 한 페이지의 url을 읽어와 제목, url, 작성자를 반환하는 함수
    # 사이트 검색 가능 판별 200 - 가능, 404 - 불가능
    site = requests.get(url)
    # 주소를 html로 표현
    site_soup = BeautifulSoup(site.text, 'lxml')
    # 뉴스 리스트 선택
    news_list = site_soup.select('div.newsbox_04')
    for news in tqdm(news_list):
        # 기사 제목
        news_title = news.select('ul.newsbox_texts > li')[0].text
        # 기사 본문 주소
        news_url = 'https://www.edaily.co.kr' + news.find('a').get('href')
        # 주소가 맞는 지 판별
        content_url = requests.get(news_url)
        # 기사 쓴 기자 이름
        news_writer = news.select('div.author_category > a')[0].text
        # 기사 작성 날짜 출력
        search_date = news.select('div.author_category')[0].text
        news_date = re.search(pattern, search_date)
        # 날짜 정규화 0000.00.00 -> 0000년 00월 00일
        newsdate_result = datetime.strptime(news_date.group(1), "%Y.%m.%d").strftime('%Y/%m/%d')

        # 기사 본문 주소
        news_url = 'https://www.edaily.co.kr' + news.find('a').get('href')
        # 주소가 맞는 지 판별
        content_url = requests.get(news_url)
        # 본문 주소 html로 표현
        content_soup = BeautifulSoup(content_url.text, 'lxml')
        # 기사 본문 내용
        content = content_soup.select('div.news_body')[0].text

        #         tag = content.find_all(['br', 'div', 'p', 'image'])

        #         for script in tag:
        #             script.extract()

        #         news_content = content.get_text('\n', strip=True)
        #         news_content = content.split('\n')  # 배열로 변환
        # 공백만 제거하고 리스트로 만들기
        text_without_spaces = "".join(content.split())
        news_content = text_without_spaces
        news_site = '이데일리'

        bul.content = news_content
        keyword_txt = bul.main()

        new_data = [news_site, news_title, news_url, news_writer, newsdate_result, news_content, keyword_txt]
        data.loc[len(data)] = new_data


def main():
    keyword = input('검색 키워드 : ')
    page = int(input('페이지 수 : '))

    for i in range(1, page + 1):
        url = makeUrl(keyword, i)
        crawlingUrl(url)

    # data['date'] = pd.to_datetime(data['date'], format="%Y년 %m월 %d일", errors='coerce') # 날짜를 datetime 형식으로 변환
    # data['date'] = data['date'].dt.strftime("%Y년 %m월 %d일")  # 날짜 형식을 변경
    data.to_csv(r'C:\AorF\edaily_news_50.csv', encoding='utf-8-sig', index=False)

main()