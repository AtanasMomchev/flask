import os
import functools

from flask import Flask, render_template, Request, request, g, redirect, url_for, session
from database import db_session
from database import init_db
from models.User import User
from pass_manager import Secrets


app = Flask(__name__)
key = os.urandom(24)
app.config.update(SECRET_KEY=key)
app.debug = True
init_db()
if not User.query.filter(User.name == 'admin').first():
    u = User("admin", "Q!w2e3r4")
    db_session.add(u)
    db_session.comit()


def login_required(func):

    @functools.wraps(func)
    def wrap(*args, **kwargs):
        if not g.user:
            return redirect(url_for("login"))
        else:
            return func(*args, **kwargs)
    return wrap


@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        user = User.query.filter(User.name == session['user_id'])
        g.user = user


@app.route('/')
@login_required
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.pop('user_id', None)

        secret = Secrets()
        username = request.form['username']
        password = request.form['password']
        db_user = User.query.filter(User.name == username).first()
        if db_user and secret.check_password(db_user.password, password.encode('utf-8')):
            session['user_id'] = db_user.name
            return redirect(url_for('index'))

        return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/create_image/ova', methods=['GET', 'POST'])
@login_required
def create_ova():
    if Request.method == 'post':
        prod = Request.form['production']
        trunk = Request.form['trunk']
        branch = Request.form['branch']
        branch_number = Request.form['branch_number']
        return [prod, trunk, branch, branch_number]
    else:
        return render_template('ova.html')


@app.route('/create_image')
@login_required
def provisioning_platform():
    return render_template('Provisioners.html')


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.run(debug=True)

