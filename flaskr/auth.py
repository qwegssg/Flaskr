# Create a Blueprint named 'auth'.
# based on cookie & session

import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

# When Flask receives a request to /auth/register, 
# it will call the register view and use the return value as the response.
@bp.route('/register', methods=('GET', 'POST'))
# register view function:
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        
        # db.execute:
        # takes a SQL query with ? placeholders for any user input, 
        # and a tuple of values to replace the placeholders with.
        # fetchone():
        # returns one row from the query. If the query returned no results, it returns None. 
        
        # It's important to always fully validate the data on the server, 
        # even if the client does some validation as well.
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif db.execute(
            'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = 'User {} is already registered.'.format(username)

        if error is None:
            db.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)',
                (username, generate_password_hash(password))
            )
            db.commit()
            return redirect(url_for('auth.login'))
        
        # flash() stores messages that can be retrieved when rendering the template.
        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        # session is a dict (key-value pair) that stores data across requests.\
        # session stores user's id
        # When validation succeeds, the user’s id is stored in a new session. 
        # The data is stored in a cookie that is sent to the browser, 
        # and the browser then sends it back with subsequent requests.
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

# At the beginning of each request, if a user is logged in,
# their information should be loaded and made available to other views.
# Thus, bp.before_app_request() registers a function 
# that runs before the view function, no matter what URL is requested.
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    # gets that user’s data from the database, storing it on g.user, 
    # which lasts for the length of the request. 
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# A decorator used to check if user is logged in or not.
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

