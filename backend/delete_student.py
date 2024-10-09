# students.py
from flask import Blueprint, request, jsonify
import MySQLdb

bp = Blueprint('students', __name__)


def get_db_connection():
    conn = MySQLdb.connect(host='localhost', user='root', passwd='123456', db='school_management', charset='utf8')
    return conn

@bp.route('/delete_student', methods=['POST'])
def delete_student():
    student_email = request.form.get('email')

    if not student_email:
        return jsonify({'success': False, 'error': 'Missing email'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM grades WHERE grade_student_epita_email_ref = %s", (student_email,))
        cursor.execute("DELETE FROM students WHERE student_epita_email = %s", (student_email,))
        conn.commit()
        return jsonify({'success': True}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()