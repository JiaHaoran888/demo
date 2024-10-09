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