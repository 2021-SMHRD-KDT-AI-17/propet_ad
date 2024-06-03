import logging
from flask import Flask, render_template, request, redirect, url_for, flash
import pymysql
import json
import os

app = Flask(__name__, template_folder='html', static_folder='static')

# 로깅 설정
logging.basicConfig(level=logging.DEBUG)

def get_top_pets():
    try:
        connection = pymysql.connect(
            host='project-db-cgi.smhrd.com',
            user='vmfhvpttj',
            password='20240621',
            database='vmfhvpttj',
            port=3307
        )
        app.logger.debug("Database connection successful")
    except pymysql.MySQLError as e:
        app.logger.error(f"Error connecting to MySQL: {e}")
        return []
    
    try:
        with connection.cursor() as cursor:
            # 상위 5개의 p_kind와 전체 count 값을 가져오는 쿼리
            sql = """
            SELECT p_kind, COUNT(p_kind) AS kind_count, (SELECT COUNT(*) FROM pet) AS total_count
            FROM pet
            GROUP BY p_kind
            ORDER BY kind_count DESC
            LIMIT 5;
            """
            cursor.execute(sql)
            rows = cursor.fetchall()
            app.logger.debug(f"Query executed successfully: {rows}")
            return rows
    except pymysql.MySQLError as e:
        app.logger.error(f"Error executing query: {e}")
        return []
    finally:
        connection.close()

@app.route('/')
def index():
    try:
        data = get_top_pets()
        # 데이터를 JSON 형식으로 변환하여 static/js 폴더에 저장
        data_json_path = os.path.join(app.static_folder, 'js', 'data.json')
        with open(data_json_path, 'w') as json_file:
            json.dump(data, json_file)

        return render_template('index.html', data=data)
    except Exception as e:
        app.logger.error(f"Error rendering template: {e}")
        
        
        return "Internal Server Error", 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('auth-login-basic.html')

@app.route('/register')
def register():
    return render_template('auth-register-basic.html')

@app.route('/account')
def account():
    return render_template('pages-account-settings-account.html')

@app.route('/notifications')
def notifications():
    return render_template('pages-account-settings-notifications.html')

@app.route('/basic')
def basic():
    return render_template('tables-basic.html')

@app.route('/user_list')
def user_list():
    return render_template('user-list.html')



if __name__ == '__main__':
    app.run(debug=True)