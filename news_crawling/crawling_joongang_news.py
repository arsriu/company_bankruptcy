from bs4 import BeautifulSoup
import requests
import pandas as pd
from tqdm.auto import tqdm
import re
from datetime import datetime


def makeUrl(keyword, n):
    url = 'https://www.joongang.co.kr/search/news?keyword=' + keyword + '&sfield=title&serviceCode=11&page=' + str(n)
    return url


def crawlingUrl(url, keyword):
    pattern = r'(\d{4}\.\d{2}\.\d{2})'
    site = requests.get(url)
    site_soup = BeautifulSoup(site.text, 'lxml')
    news_list = site_soup.select('ul.story_list > li.card')

    # "유료 전용" 태그가 있는 기사를 먼저 검사하여 제외
    news_list = [news for news in news_list if not news.select('strong.badge_plus')]

    for news in tqdm(news_list):
        try:
            # 기사 제목 추출
            news_title = news.select('h2.headline')[0].text
            news_title = news_title.replace('\n', '')

            # 기사 URL 추출
            news_url_suffix = news.find('a').get('href')
            if not news_url_suffix.startswith('https://www.joongang.co.kr'):
                news_url_suffix = 'https://www.joongang.co.kr' + news_url_suffix
            news_url = news_url_suffix

            # 기사 내용 가져오기
            content_url = requests.get(news_url)
            try:
                content_soup = BeautifulSoup(content_url.content, 'lxml', from_encoding=content_url.encoding)
            except UnicodeDecodeError:
                content_soup = BeautifulSoup(content_url.content, 'lxml', from_encoding='latin-1')

            # 기사 쓴 기자 이름
            news_writer_element = content_soup.find('div', {'class': 'byline'})
            if news_writer_element and news_writer_element.find('a'):
                news_writer = news_writer_element.find('a').text.replace('기자', '')
            else:
                news_writer = 'AI 기사'

            # 기사 작성 날짜 출력
            search_date = news.select('p.date')[0].text
            news_date = re.search(pattern, search_date)

            if news_date:
                news_date_result = datetime.strptime(news_date.group(1), "%Y.%m.%d").strftime('%Y-%m-%d')
            else:
                news_date_result = None

            # 기사 내용 추출
            content_element = content_soup.select('div.article_body')[0]
            news_content = content_element.get_text(separator='', strip=True)  # 줄 바꿈을 제거하기 위해 separator를 빈 문자열로 설정

            name = keyword

            # 데이터프레임에 추가
            new_data = [name, news_title, news_url, news_writer, news_date_result, news_content]
            data.loc[len(data)] = new_data

        except Exception as e:
            continue

def main():
    # 사용자 입력 받기
    keyword = input('검색 키워드: ')
    n = int(input('페이지 수: '))

    # 데이터프레임 초기화
    global data
    data = pd.DataFrame(columns=['name', 'title', 'url', 'writer', 'date', 'content'])

    # 크롤링 실행
    for i in range(1, n + 1):
        url = makeUrl(keyword, i)
        crawlingUrl(url, keyword)

    # 'date' 열을 날짜 형식으로 변환
    data['date'] = pd.to_datetime(data['date'], errors='coerce').dt.strftime('%Y-%m-%d')

    # CSV 파일로 저장
    data.to_csv(r'C:\Python\goorm\hani_news.csv', encoding='utf-8-sig', index=False)


main()