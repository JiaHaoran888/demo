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