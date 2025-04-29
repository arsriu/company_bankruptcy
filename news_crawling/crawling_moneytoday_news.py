from bs4 import BeautifulSoup
import requests
import pandas as pd
from tqdm.auto import tqdm
from datetime import datetime
from urllib.parse import quote

data = pd.DataFrame(columns=['name', 'title', 'url', 'writer', 'date', 'content'])


def makeUrl(keyword, n):  # 입력한 페이지의 URL을 변환하는 함수
    query = quote(keyword, encoding='euc-kr')
    url = 'https://search.mt.co.kr/searchNewsList.html?srchFd=T&range=TOTAL&category=MTNW&reSrchFlag=&preKwd=&search_type=m&kwd=' + query + '&bgndt=&enddt=&category=MTNW&sortType=allwordsyn&subYear=&category=MTNW&subType=mt&pageNum=' + str(n)
    return url

def crawlingUrl(url, keyword):
    site = requests.get(url)
    site_soup = BeautifulSoup(site.text, 'lxml')
    news_list = site_soup.find('div', {'class': 'section'}).find_all('li')
    for news in tqdm(news_list):
        news_url = news.find('strong', {'class': 'subject'}).find('a')
        news_url = news_url.get('href')
        content_url = requests.get(news_url)
        content_soup = BeautifulSoup(content_url.text, 'lxml')
        news_title = news.select('strong.subject')[0].text
        content = content_soup.select_one('div#textBody')
        for tr in content.find_all('tr'):
            tr.decompose()  # tr 태그 제거
        text = content.get_text(strip=True)  # 기사 본문
        news_writer = content_soup.find('li', {'class': 'name'}).text  # 저자
        search_date = content_soup.select('li.date')[0].text  # 시간
        name = keyword

        # 날짜 형식 변경
        news_date = datetime.strptime(search_date, "%Y.%m.%d %H:%M").strftime('%Y-%m-%d')

        new_data = [name, news_title, news_url, news_writer, news_date, text]
        data.loc[len(data)] = new_data


def main():
    keyword = input('검색 키워드 : ')
    n = int(input('페이지 수 : '))

    for i in range(1, n + 1):
        url = makeUrl(keyword, i)
        crawlingUrl(url, keyword)

    data.to_csv(r'C:\AorF\test.csv', encoding='utf-8-sig', index=False)


if __name__ == "__main__":
    main()