# The __init__.py serves double duty: 
# it will contain the application factory, and it tells Python 
# that the flaskr directory should be treated as a package.

# Creating a global Flask instance directly can cause some 
# tricky issues as the project grows. Therefore, we create 
# Flask instance inside a function -- application factory.

# Application factory:
# A function that any configuration, registration, 
# and other setup the application needs will happen inside the function, 
# then the application will be returned.

import os

from flask import Flask


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    # The instance folder is located outside the flaskr package 
    # and can hold local data that shouldn't be committed to version control,
    # such as configuration secrets and the database file.
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    from . import db
    db.init_app(app)

    # The authentication blueprint will have views 
    # to register new users and to log in and log out.
    from . import auth
    app.register_blueprint(auth.bp)

    return app