# 默认路由
@app.route('/')
def index():
    return redirect(url_for('login'))