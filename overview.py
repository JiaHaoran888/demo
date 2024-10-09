from flask import Blueprint, render_template
import MySQLdb
from datetime import datetime

bp = Blueprint('overview', __name__)

def get_db_connection():
    conn = MySQLdb.connect(host='localhost', user='root', passwd='123456', db='school_management', charset='utf8')
    return conn

@bp.route('/overview')
def overview():
    conn = get_db_connection()
    cur = conn.cursor()

    # 获取学生总数和课程数量
    cur.execute(''' 
        SELECT 
            COUNT(DISTINCT student_epita_email) AS total_students,
            COUNT(DISTINCT course_code) AS total_courses
        FROM students s
        JOIN enrollments e ON s.student_epita_email = e.enrollment_student_ref
    ''')
    stats = cur.fetchone()

    # 获取每个课程的平均出勤率
    cur.execute(''' 
        SELECT 
            c.course_code,
            COALESCE((SUM(a.attendance_presence) / NULLIF(COUNT(*), 0)) * 100, 0) AS average_attendance
        FROM courses c
        LEFT JOIN enrollments e ON c.course_code = e.enrollment_course_ref
        LEFT JOIN attendance a ON e.enrollment_student_ref = a.attendance_student_ref
        GROUP BY c.course_code
    ''')
    course_attendance = cur.fetchall()

    # 上次更新的日期（静态示例）
    last_update_date = datetime(2024, 10, 1).strftime('%Y-%m-%d')

    cur.close()
    conn.close()

    return render_template('overview.html', stats=stats, course_attendance=course_attendance, last_update_date=last_update_date)
