# students.py
from flask import Blueprint, request, jsonify
import MySQLdb

bp = Blueprint('students', __name__)



@bp.route('/update_student', methods=['POST'])
def edit_student():
    student_email = request.form.get('email')
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')

    if not student_email or not first_name or not last_name:
        return jsonify({'success': False, 'error': 'Missing data'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE contacts
            SET contact_first_name = %s, contact_last_name = %s
            WHERE contact_email = (SELECT student_contact_ref FROM students WHERE student_epita_email = %s)
        """, (first_name, last_name, student_email))
        conn.commit()
        return jsonify({'success': True}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()