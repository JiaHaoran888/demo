
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

