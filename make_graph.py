import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager, rc
import sqlite3

# 한국어 폰트 설정
font_path = "C:/Windows/Fonts/malgun.ttf"  # 맑은 고딕 경로에 맞게 수정
font_name = font_manager.FontProperties(fname=font_path).get_name()
rc('font', family=font_name)


# 등급 산출
def calculate_grade(trend_angle):
    if trend_angle >= 80:
        return 'S'
    elif trend_angle >= 60:
        return 'A'
    elif trend_angle >= 40:
        return 'B'
    elif trend_angle >= 20:
        return 'C'
    else:
        return 'F'

def connect_to_db():
    conn = sqlite3.connect(r'C:\A+orF\news.db')
    return conn


def close_connection(conn):
    conn.close()


def get_data_from_db(conn, input_word):
    # SQLite 데이터베이스에서 데이터를 가져오는 쿼리 작성
    query = f"SELECT * FROM default_rate WHERE title LIKE '%{input_word}%'"
    df = pd.read_sql_query(query, conn)
    return df


def main(input_word):
    conn = connect_to_db()
    # CSV 파일을 데이터프레임으로 읽어오기
    df = get_data_from_db(conn, input_word)

    # 'title' 컬럼에서 입력한 단어를 포함하는 행만 추출
    filtered_df = df[df['title'].str.contains(input_word, case=False, na=False)].copy()

    # date 컬럼을 datetime 형식으로 변환 (errors='coerce'를 사용하여 파싱 오류를 NaT로 대체)
    filtered_df['date'] = pd.to_datetime(filtered_df['date'], format="%Y-%m-%d", errors='coerce')

    # NaT가 아닌 행만 선택
    filtered_df = filtered_df[~filtered_df['date'].isna()]

    # date가 2020년 이후인 행들만 선택
    filtered_df = filtered_df[filtered_df['date'].dt.year >= 2017]

    # date를 기준으로 데이터프레임 정렬
    filtered_df.sort_values(by='date', inplace=True)

    # 최근 10개 기사 선택
    recent_articles = filtered_df.tail(10)

    # 최근 10개 기사의 'default_rate(%)' 열 평균 계산
    recent_articles_num = np.mean(recent_articles['default_rate']) 

    # 월별 평균 연체율 계산
    monthly_avg_df = filtered_df.groupby(filtered_df['date'].dt.to_period("M")).mean(numeric_only=True)

    # 추세선 추가
    z = np.polyfit(np.arange(len(monthly_avg_df)), monthly_avg_df['default_rate'], 1)
    p = np.poly1d(z)
    trend_line = p(np.arange(len(monthly_avg_df)))

    # 추세선 각도 계산
    trend_angle = np.degrees(np.arctan(z[0]))

    if trend_angle >= 0:
        angle_result = abs(50 - recent_articles_num) * -2
    else:
        angle_result = abs(50 - recent_articles_num) * 2

    total_avg = round(monthly_avg_df['default_rate'].mean(), 0)

    # 전체 평균 연체율 수평선 추가 (y=48.648)
    avg_line = np.full_like(monthly_avg_df['default_rate'], fill_value=total_avg)

    # 전체 평균 연체율 각도 계산
    avg_angle = 0

    total_result = angle_result + 50

    # 결과 출력
    print(f"'{input_word}'에 대한 월별 평균 부도확률:")
    print(recent_articles_num)
    print("월 평균에 따른 추세선의 각도:", trend_angle)
    # 등급 계산 및 출력
    trend_grade = calculate_grade(total_result)
    print("기업 점수:", total_result)
    print("기업 재정 등급:", trend_grade)
    print("-----------------------------")

    # 그래프 시각화
    plt.figure(figsize=(10, 6))
    plt.plot(monthly_avg_df.index.astype(str), monthly_avg_df['default_rate'], marker='o', linestyle='-',
             label='월별 평균 연체율')

    # 추세선 그리기
    plt.plot(monthly_avg_df.index.astype(str), trend_line, 'r--', label='추세선')

    # 전체 평균 연체율 수평선 추가
    plt.plot(monthly_avg_df.index.astype(str), avg_line, 'g-', label='임계값')

    plt.title(f'"{input_word}"의 시간에 따른 월별 평균 부도확률')
    plt.xlabel('월')
    plt.ylabel('월별 평균 부도확률 (%)')
    plt.grid(True)
    plt.xticks(rotation=45, ha='right')  # x 축 레이블 회전
    plt.legend()  # 범례 추가
    plt.tight_layout()
    output_image_path = f'static/graph/{input_word}.png'
    plt.savefig(output_image_path)

    close_connection(conn)

    result_percent = recent_articles_num
    
    group_rating = trend_grade

    return output_image_path, total_result, group_rating