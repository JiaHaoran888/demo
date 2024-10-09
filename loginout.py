from flask import session, redirect, url_for, flash

@app.route('/logout')
def logout():
    # 清除会话
    session.pop('user_id', None)  # 假设你用 'user_id' 存储用户的 ID
    flash('You have been logged out successfully.')
    return redirect(url_for('login'))
