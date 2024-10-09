# students.py
from flask import Blueprint, request, jsonify
import MySQLdb

bp = Blueprint('students', __name__)


def get_db_connection():
    conn = MySQLdb.connect(host='localhost', user='root', passwd='123456', db='school_management', charset='utf8')
    return conn


@bp.route('/add_student', methods=['POST'])
def add_student():
    email = request.form.get('email')
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')

    if not email or not first_name or not last_name:
        return jsonify({'success': False, 'error': 'Missing data'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO contacts (contact_email, contact_first_name, contact_last_name) VALUES (%s, %s, %s)",
            (email, first_name, last_name))
        cursor.execute(
            "INSERT INTO students (student_epita_email, student_contact_ref, student_enrollment_status) VALUES (%s, %s, %s)",
            (email, email, 'Enrolled'))
        conn.commit()
        return jsonify({'success': True}), 200
    except MySQLdb.IntegrityError as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()






