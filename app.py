from flask import Flask, g, render_template, request, session, redirect, url_for, flash, jsonify
import matplotlib
import make_graph
import sqlite3

matplotlib.use('Agg')  # 백엔드 설정

app = Flask(__name__)
app.secret_key = 'news_db'
app.config['DATABASE'] = r'C:\A+orF\news.db'  # SQLite 데이터베이스 파일 경로에 맞게 수정


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = sqlite3.Row
    return db


def close_db(e=None):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.before_request
def before_request():
    g.db = get_db()


@app.teardown_appcontext
def teardown_appcontext(exception):
    close_db()


# 테이블 선택
user_table = 'userTable'


# 로그인 및 회원가입 구현
@app.route('/', methods=['GET', 'POST'])
def start():
    if request.method == 'POST':
        if 'signInId' in request.form:  # Sign-in form submitted
            inId = request.form['signInId']
            inPw = request.form['signInPw']

            # 커서 생성
            with g.db:
                cursor = g.db.cursor()
                query = f"SELECT * FROM {user_table} WHERE id = ? AND password = ?"
                cursor.execute(query, (inId, inPw))
                result = cursor.fetchone()

            if result:
                with g.db:
                    cursor = g.db.cursor()
                    namequery = f"SELECT name FROM {user_table} WHERE id = ?"
                    cursor.execute(namequery, (inId,))
                    rsName = cursor.fetchone()

                if rsName:
                    session['signInId'] = rsName[0]
                    return redirect(url_for('index'))
                else:
                    # 예외 처리: 해당 ID에 대한 이름이 없을 때의 처리
                    flash('로그인 실패. 사용자 이름 또는 비밀번호를 확인하세요.', 'error')
            else:
                # 로그인 실패 시 플래시 메시지
                flash('사용자 이름 또는 비밀번호를 확인하세요.', 'error')

        elif 'signUpId' in request.form:  # Sign-up form submitted
            upId = request.form.get('signUpId')
            upPw = request.form.get('password')
            upName = request.form.get('name')
            upEmail = request.form.get('email')
            upPhone = request.form.get('phone-num')

            # 커서 생성
            with g.db:
                cursor = g.db.cursor()
                query = f"INSERT INTO {user_table} (id, password, name, email, phone_number) VALUES (?, ?, ?, ?, ?)"
                cursor.execute(query, (upId, upPw, upName, upEmail, upPhone))
                g.db.commit()

            # flash('회원가입 성공!', 'success')

    return render_template('start.html')  # 이 부분에 메인 페이지의 HTML 파일명을 넣어주세요


@app.route('/logout')
def logout():
    if 'signInId' in session:
        # 세션에서 사용자 정보 삭제
        session.pop('signInId', None)
    return redirect('/')


# 대기 화면
@app.route('/index')
def index():
    if 'signInId' in session:
        username = session['signInId']
        return render_template('index.html', image_path=None, user=username)


# 메인 페이지
@app.route('/main')
def main():
    if 'signInId' in session:
        username = session['signInId']
        return render_template('main.html', user=username)


@app.route('/update_image', methods=['POST'])
def update_image():
    input_word = request.form['news_input']

    # make_graph.py 실행
    try:
        # path = make_graph.main(input_word)
        path, result_percent, group_rating = make_graph.main(input_word)
    except:
        path = f'static/image/notitle.png'
        result_percent = 0
        group_rating = None
        return jsonify(output_image_path=path, result_percent=result_percent, group_rating=group_rating)

    # 이미지 파일 경로
    output_image_path = f'static/graph/{input_word}.png'

    # 그래프 이미지를 생성
    # create_graph(path, output_image_path)

    # 이미지 파일의 경로를 반환

    return jsonify(output_image_path=output_image_path, result_percent=result_percent, group_rating=group_rating)


if __name__ == '__main__':
    # 외부에서 접속 가능한 모든 IP 주소, 포트 8000으로 설정
    app.run(port=5000, debug=True)
