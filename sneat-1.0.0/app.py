import logging
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import pymysql
import json
import os

app = Flask(__name__, template_folder='html', static_folder='static')

# 로깅 설정
logging.basicConfig(level=logging.DEBUG)

def get_users():
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
            sql = """
            SELECT 
                u.u_id, 
                u.u_name, 
                u.u_phone,
            CASE 
                    WHEN p.u_idx IS NOT NULL THEN 'Y' 
                    ELSE 'N' 
                END AS pet_status,
                (SELECT COUNT(*) FROM users) AS total
            FROM 
                users u
            LEFT OUTER JOIN 
                pet p
            ON 
                u.u_idx = p.u_idx;
            """
            cursor.execute(sql)
            rows = cursor.fetchall()
            app.logger.debug(f"Users query executed successfully: {rows}")
            return rows
    except pymysql.MySQLError as e:
        app.logger.error(f"Error executing query: {e}")
        return []
    finally:
        connection.close()



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

def get_questions():
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
            sql = """
            SELECT q_content, q_answer, q_tf, u_id 
            FROM question 
            JOIN users ON question.u_idx = users.u_idx;
            """
            cursor.execute(sql)
            rows = cursor.fetchall()
            app.logger.debug(f"Questions query executed successfully: {rows}")
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
        questions = get_questions()
        users = get_users()

        
        # com과 incom 계산
        com = sum(1 for row in questions if row[2] == 'Y')
        incom = sum(1 for row in questions if row[2] == 'N')

        data_json_path = os.path.join(app.static_folder, 'js', 'data.json')
        with open(data_json_path, 'w') as json_file:
            json.dump(data, json_file)

        questions_json_path = os.path.join(app.static_folder, 'js', 'questions.json')
        with open(questions_json_path, 'w') as json_file:
            json.dump({"com": com, "incom": incom}, json_file)

        return render_template('index.html', users = users,data=data, questions=questions, com=com, incom=incom)
    except Exception as e:
        app.logger.error(f"Error rendering template: {e}")
        return "Internal Server Error", 500

@app.route('/basic')
def basic():
    try:
        questions = get_questions()
        
        # com과 incom 계산
        com = sum(1 for row in questions if row[2] == 'Y')
        incom = sum(1 for row in questions if row[2] == 'N')

        return render_template('tables-basic.html', questions=questions, com=com, incom=incom)
    except Exception as e:
        app.logger.error(f"Error rendering template: {e}")
        return "Internal Server Error", 500

@app.route('/user_list')
def user_list():
    try:
        users = get_users()
        return render_template('user-list.html',users = users)
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

if __name__ == '__main__':
    app.run(debug=True)
