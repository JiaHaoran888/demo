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