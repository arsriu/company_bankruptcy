import pandas as pd
import re
import ast
import pickle
from keras.models import load_model
from keras.preprocessing.sequence import pad_sequences
import re
from konlpy.tag import Okt
import numpy as np


data = pd.DataFrame(columns=['name', 'title', 'url', 'writer', 'date', 'content', 'content_list', 'default_rate(%)'])


def sentiment_predict(new_sentence, loaded_model, tokenizer, max_len):
    okt = Okt()
    stopwords = ['의', '가', '이', '은', '들', '는', '좀', '잘', '걍', '과', '도', '를', '으로', '자', '에', '와', '한', '하다']

    new_sentence = re.sub(r'[^ㄱ-ㅎㅏ-ㅣ가-힣 ]', '', new_sentence)
    new_sentence = okt.morphs(new_sentence, stem=True)
    new_sentence = [word for word in new_sentence if not word in stopwords]

    encoded = tokenizer.texts_to_sequences([new_sentence])
    pad_new = pad_sequences(encoded, maxlen=max_len)
    score = float(loaded_model.predict(pad_new))

    return score


if __name__ == "__main__":
    # 모델과 토크나이저 로드
    loaded_model = load_model('../../model/best_model.h5')
    with open('../../model/tokenizer.pickle', 'rb') as handle:
        tokenizer = pickle.load(handle)

    csv_file_path = r'C:\AorF\news_absorptions_list.csv'
    # pandas를 사용하여 CSV 파일 로드
    df = pd.read_csv(csv_file_path)
    for i in range(30000, 33000):
        total = 0
        name = df['name'][i]
        title = df['title'][i]
        url = df['url'][i]
        writer = df['writer'][i]
        date = df['date'][i]
        content = df['content'][i]

        content_list = ast.literal_eval(df['content_list'][i])

        for text in content_list:
            result = sentiment_predict(text, loaded_model, tokenizer, max_len=100)
            default_percent = round((1-result) * 100, 2)
            total += default_percent

        default_rate = total / len(content_list)

        new_data = [name, title, url, writer, date, content, content_list, round(default_rate, 2)]
        data.loc[len(data)] = new_data
        print(i)

    data.to_csv(r'C:\A+orF\default_rate_30000.csv', encoding='utf-8-sig', index=False)

