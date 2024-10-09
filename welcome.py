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
