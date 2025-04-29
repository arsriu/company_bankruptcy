import pandas as pd
import re

result_articles = []  # 각 기사를 문장 리스트로 저장하는 리스트

def split_sentences_from_dataframe(df):
    exclusion_pattern1 = r"\(서울=뉴스1\) [가-힣]+ 기자"
    exclusion_pattern2 = r"<저작권자 © 뉴스1코리아, 무단전재 및 재배포 금지>"

    for content in df['content']:
        if isinstance(content, str):  # Check if 'content' is a string
            sentences = re.split(r'[.!?]', content)  # 마침표, 물음표, 느낌표로 문장 나누기
            article_sentences = []

            for sentence in sentences:
                if not (re.search(exclusion_pattern1, sentence) or re.search(exclusion_pattern2, sentence)):
                    sentence = sentence.replace("━", "")
                    match = re.search(r'\d+\.\d+', sentence)
                    if match:
                        number_with_decimal = match.group()
                        sentence = sentence.replace(number_with_decimal, number_with_decimal + "㎛")
                    sentence = sentence.strip()
                    sentence = re.sub(r'\b기자\b', '', sentence)
                    sentence = re.sub(r'\b\w+\@\w+\.\w+\b', '', sentence)
                    if 'co.' in sentence or 'kr' in sentence or 'Q.' in sentence or 'A.' in sentence:
                        continue
                    article_sentences.append(sentence)

            result_articles.append(article_sentences)
        else:
            result_articles.append([])  # If 'content' is not a string, append an empty list

    return result_articles

if __name__ == "__main__":
    csv_file_path = r'C:\AorF\news_absorptions.csv'
    df = pd.read_csv(csv_file_path)

    # 함수 호출하여 각 기사를 문장 리스트로 저장하는 리스트 획득
    result_articles = split_sentences_from_dataframe(df)

    # 'Extracted Sentences'를 8번째 컬럼으로 추가
    df.insert(6, 'content_list', result_articles)

    # UTF-8 인코딩 및 BOM을 포함하여 새 CSV 파일로 DataFrame 저장
    result_csv_path = r'C:\AorF\news_absorptions_list.csv'  # 새로운 CSV 파일의 경로 지정
    df.to_csv(result_csv_path, index=False, encoding='utf-8-sig', quoting=1)  # quoting=1을 추가하여 리스트를 문자열로 변환

    print(f"추출된 문장이 {result_csv_path}에 리스트 형식으로 추가되었습니다.")