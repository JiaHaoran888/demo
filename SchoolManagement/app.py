from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
import MySQLdb
from datetime import datetime
import MySQLdb.cursors

app = Flask(__name__)

# 数据库连接
def get_db_connection():
    conn = MySQLdb.connect(host='localhost', user='root', passwd='123456', db='school_management', charset='utf8'
                           )  # 设置 cursorclass 为 DictCursor
    return conn

conn = get_db_connection()
cursor = conn.cursor()
# 默认路由
@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)

        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user:
            return redirect(url_for('welcome'))
        else:
            flash('Invalid username or password.')

    return render_template('login.html')




@app.route('/welcome')
def welcome():
    conn = get_db_connection()
    cur = conn.cursor()

    # 获取学生人数
    cur.execute('''
        SELECT 
            p.population_code,
            p.population_year,
            p.population_period,
            COUNT(s.student_epita_email) AS student_count
        FROM populations p
        LEFT JOIN students s ON s.student_population_code_ref = p.population_code
                             AND s.student_population_year_ref = p.population_year
                             AND s.student_population_period_ref = p.population_period
        GROUP BY p.population_code, p.population_year, p.population_period
    ''')
    populations = cur.fetchall()

    # 获取总体出勤率
    cur.execute('''
        SELECT 
            p.population_code,
            p.population_year,
            p.population_period,
            COALESCE((SUM(a.attendance_presence) / NULLIF(COUNT(*), 0)) * 100, 0) AS attendance_percentage
        FROM attendance a
        JOIN students s ON a.attendance_student_ref = s.student_epita_email
        JOIN populations p ON s.student_population_code_ref = p.population_code
                            AND s.student_population_year_ref = p.population_year
                            AND s.student_population_period_ref = p.population_period
        GROUP BY p.population_code, p.population_year, p.population_period
    ''')
    attendance = cur.fetchall()

    # 上次网站构建的日期（静态示例）
    last_build_date = datetime(2024, 9, 14).strftime('%Y-%m-%d')

    cur.close()
    conn.close()

    return render_template('welcome.html', populations=populations, attendance=attendance, last_build_date=last_build_date)

# Route to view the population page
# 获取学生及课程数据


# @app.route('/edit_student', methods=['POST'])
# def edit_student():
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     student_email = request.form['email']
#     first_name = request.form['first_name']
#     last_name = request.form['last_name']
#
#     query_update = """
#     UPDATE contacts
#     SET contact_first_name = %s, contact_last_name = %s
#     WHERE contact_email = (SELECT student_contact_ref FROM students WHERE student_epita_email = %s)
#     """
#     cursor.execute(query_update, (first_name, last_name, student_email))
#     conn.commit()
#     cursor.close()
#     conn.close()
#
#     return jsonify({'success': True})

@app.route('/update_student', methods=['POST'])
def edit_student():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        student_email = request.form['email']
        first_name = request.form['first_name']
        last_name = request.form['last_name']

        query_update = """
        UPDATE contacts
        SET contact_first_name = %s, contact_last_name = %s
        WHERE contact_email = (SELECT student_contact_ref FROM students WHERE student_epita_email = %s)
        """
        cursor.execute(query_update, (first_name, last_name, student_email))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'success': True})

    except Exception as e:
        print(f'Error: {e}')  # Log the error
        return jsonify({'success': False, 'error': str(e)})



@app.route('/delete_student', methods=['POST'])
def delete_student():
    conn = get_db_connection()
    cursor = conn.cursor()
    student_email = request.form['email']

    query_delete_grades = "DELETE FROM grades WHERE grade_student_epita_email_ref = %s"
    cursor.execute(query_delete_grades, (student_email,))

    query_delete_student = "DELETE FROM students WHERE student_epita_email = %s"
    cursor.execute(query_delete_student, (student_email,))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'success': True})

@app.route('/population/<population_code>/<population_year>/<population_period>')
def population(population_code, population_year, population_period):
    conn = get_db_connection()
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)

    # Get student list and grades
    query_students = """
    SELECT s.student_epita_email, c.contact_first_name, c.contact_last_name,
           SUM(CASE WHEN g.grade_score >= 50 THEN 1 ELSE 0 END) AS passed_courses,
           SUM(CASE WHEN g.grade_score < 50 THEN 1 ELSE 0 END) AS failed_courses
    FROM students s
    JOIN contacts c ON s.student_contact_ref = c.contact_email
    LEFT JOIN grades g ON s.student_epita_email = g.grade_student_epita_email_ref
    WHERE s.student_population_code_ref = %s
      AND s.student_population_year_ref = %s
      AND s.student_population_period_ref = %s
    GROUP BY s.student_epita_email
    """
    cursor.execute(query_students, (population_code, population_year, population_period))
    students = cursor.fetchall()

    # Get course list
    query_courses = """
    SELECT p.program_course_code_ref, c.course_name, c.course_description
    FROM programs p
    JOIN courses c ON p.program_course_code_ref = c.course_code
       AND p.program_course_rev_ref = c.course_rev
    WHERE p.program_assignment = %s
    """
    cursor.execute(query_courses, (population_code,))
    courses = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('population.html', students=students, courses=courses, population_code=population_code, population_year=population_year, population_period=population_period)

@app.route('/add_student', methods=['POST'])
def add_student():
    email = request.form.get('email')
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    population_code = request.form.get('population_code')
    population_year = request.form.get('population_year')
    population_period = request.form.get('population_period')
    print(email, first_name, last_name, population_code, population_year, population_period)

    if not email or not first_name or not last_name:
        return jsonify({'success': False, 'error': 'Missing data'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Check if the email already exists in contacts
        cursor.execute("SELECT COUNT(*) FROM contacts WHERE contact_email = %s", (email,))
        email_exists = cursor.fetchone()[0] > 0

        if not email_exists:
            # Insert into contacts
            cursor.execute("INSERT INTO contacts (contact_email, contact_first_name, contact_last_name) VALUES (%s, %s, %s)", (email, first_name, last_name))

        # Insert into students table
        cursor.execute("""
            INSERT INTO students (student_epita_email, student_contact_ref, student_enrollment_status, student_population_period_ref, student_population_year_ref, student_population_code_ref)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (email, email, 'Enrolled', population_period, population_year, population_code))

        conn.commit()
        return jsonify({'success': True}), 200
    except MySQLdb.IntegrityError as e:
        error_message = str(e)
        print("MySQL IntegrityError occurred:", error_message)
        print("Traceback:", traceback.format_exc())
        conn.rollback()
        return jsonify({'success': False, 'error': 'Database integrity error: ' + error_message}), 500
    except Exception as e:
        error_message = str(e)
        print("An error occurred:", error_message)
        print("Traceback:", traceback.format_exc())
        conn.rollback()
        return jsonify({'success': False, 'error': 'An error occurred: ' + error_message}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/search_student', methods=['GET'])
def search_student():
    query = request.args.get('query', '')
    population_code = request.args.get('population_code', '')

    if not query or not population_code:
        return jsonify({'students': [], 'error': 'Missing query or population code'}), 400

    conn = get_db_connection()
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)

    # SQL query to search students based on name and population code
    sql_query = """
    SELECT s.student_epita_email, c.contact_first_name, c.contact_last_name
    FROM students s
    JOIN contacts c ON s.student_contact_ref = c.contact_email
    WHERE s.student_population_code_ref = %s
      AND (c.contact_first_name LIKE %s OR c.contact_last_name LIKE %s)
    """

    search_pattern = f'%{query}%'
    cursor.execute(sql_query, (population_code, search_pattern, search_pattern))
    students = cursor.fetchall()
    print(students)

    cursor.close()
    conn.close()

    return jsonify({'students': students})



# 课程页面
@app.route('/courses/<course_code>/grades/<population_code>')
def view_course_grades(course_code, population_code):
    # Logic to handle the request
    pass


import traceback


@app.route('/add_and_assign_course', methods=['POST'])
def add_and_assign_course():
    conn = None
    cursor = None
    try:
        course_name = request.form.get('course_name')
        course_code = request.form.get('course_code')
        population_code = request.form.get('population_code')
        population_year = request.form.get('population_year')
        population_period = request.form.get('population_period')
        print(course_name, course_code, population_code, population_year, population_period)

        if not course_name or not course_code or not population_code or not population_year or not population_period:
            return jsonify({'success': False, 'error': 'Missing data'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert into courses
        cursor.execute("INSERT INTO courses (course_code, course_name, course_rev) VALUES (%s, %s, %s)", (course_code, course_name, 1))

        # Assign course to population
        cursor.execute(
            "INSERT INTO programs (program_course_code_ref, program_course_rev_ref, program_assignment) VALUES (%s, %s, %s)",
            (course_code, 1, population_code))

        conn.commit()
        return jsonify({'success': True}), 200
    except Exception as e:
        # Log the detailed traceback
        error_message = str(e)
        print("An error occurred:", error_message)
        print("Traceback:", traceback.format_exc())

        if conn is not None:
            conn.rollback()

        return jsonify({'success': False, 'error': error_message}), 500
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()

@app.route('/search_and_assign_course', methods=['POST'])
def search_and_assign_course():
    try:
        search_query = request.form.get('search_query')
        population_code = request.form.get('population_code')
        print(search_query, population_code)

        if not search_query or not population_code:
            return jsonify({'success': False, 'error': 'Missing data'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if the course exists by name or code
        cursor.execute("""
            SELECT course_code, course_rev 
            FROM courses 
            WHERE course_code = %s OR course_name LIKE %s
        """, (search_query, f'%{search_query}%'))
        courses = cursor.fetchall()

        if not courses:
            return jsonify({'success': False, 'error': 'Course not found'}), 404

        # Assign course to population
        for course_code, course_rev in courses:
            # Check if the entry already exists
            cursor.execute("""
                SELECT COUNT(*) 
                FROM programs 
                WHERE program_course_code_ref = %s AND program_course_rev_ref = %s AND program_assignment = %s
            """, (course_code, course_rev, population_code))
            count = cursor.fetchone()[0]

            if count == 0:
                cursor.execute("""
                    INSERT INTO programs (program_course_code_ref, program_course_rev_ref, program_assignment)
                    VALUES (%s, %s, %s)
                """, (course_code, course_rev, population_code))
            else:
                # Optionally, you could update the existing entry instead
                print(f"Entry already exists for {course_code}, {course_rev}, {population_code}")

        conn.commit()
        return jsonify({'success': True, 'courses': courses}), 200
    except MySQLdb.IntegrityError as e:
        # Log the detailed traceback
        error_message = str(e)
        print("An error occurred:", error_message)
        print("Traceback:", traceback.format_exc())

        conn.rollback()
        return jsonify({'success': False, 'error': error_message}), 500
    except Exception as e:
        # Log the detailed traceback
        error_message = str(e)
        print("An error occurred:", error_message)
        print("Traceback:", traceback.format_exc())

        conn.rollback()
        return jsonify({'success': False, 'error': error_message}), 500
    finally:
        cursor.close()
        conn.close()

import secrets
print(secrets.token_hex(16))  # 生成一个 32 字节的密钥（64 个十六进制字符）
app.secret_key = secrets.token_hex(16)
@app.route('/courses', methods=['GET', 'POST'])
def courses():
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        student_email = request.form['student_email']
        course_code = request.form['course_code']
        course_rev = request.form['course_rev']
        exam_type = request.form['exam_type']
        new_grade = request.form['grade']
        print(student_email, course_code, course_rev, exam_type, new_grade)

        if new_grade == '':
            new_grade = None

        if new_grade is None:
            cur.execute(
                'UPDATE grades SET grade_score = NULL WHERE grade_student_epita_email_ref = %s AND grade_course_code_ref = %s AND grade_course_rev_ref = %s AND grade_exam_type_ref = %s',
                (student_email, course_code, course_rev, exam_type))
        else:
            cur.execute('REPLACE INTO grades (grade_student_epita_email_ref, grade_course_code_ref, grade_course_rev_ref, grade_exam_type_ref, grade_score) VALUES (%s, %s, %s, %s, %s)',
                        (student_email, course_code, course_rev, exam_type, new_grade))

        conn.commit()
        flash('Grades updated successfully!')
        return redirect(url_for('courses'))

    # 查询所有课程
    cur.execute('SELECT course_code, course_rev, course_name FROM courses ORDER BY course_code, course_rev')
    courses = cur.fetchall()
    print(courses)

    # 查询所有学生和他们的成绩
    cur.execute('''
        SELECT s.student_epita_email, c.course_code, c.course_rev, g.grade_exam_type_ref, g.grade_score
        FROM students s
        LEFT JOIN grades g ON s.student_epita_email = g.grade_student_epita_email_ref
        LEFT JOIN courses c ON g.grade_course_code_ref = c.course_code AND g.grade_course_rev_ref = c.course_rev
        ORDER BY s.student_epita_email, c.course_code, c.course_rev, g.grade_exam_type_ref
    ''')
    grades = cur.fetchall()
    print(grades)

    conn.close()
    return render_template('courses.html', grades=grades, courses=courses)


# 成绩页面
@app.route('/grades')
def grades():
    return render_template('grades.html')

if __name__ == '__main__':
    app.run(debug=True)
