
"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
        python3 server.py
Go to http://localhost:8000 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
# accessible as a variable in index.html:
from collections import defaultdict
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import Session
from flask import Flask, request, render_template, g, redirect, Response
from flask import json
from sqlalchemy.ext.automap import automap_base

tmpl_dir = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
app.jinja_env.filters['zip'] = zip
Base = automap_base()


# DATABASEURI = mysql://username:password@server/db
# DATABASEURI = "mysql+pymysql://21fa_yzhou193:E1hL7yOSEP@dbase.cs.jhu.edu/21fa_yzhou193_db"
DATABASEURI = os.environ.get('DB_CONNECTION_STRING')


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

# reflect the tables
Base.prepare(engine, reflect=True)

session = Session(engine)
#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#


@app.before_request
def before_request():
    """
    This function is run at the beginning of every web request 
    (every time you enter an address in the web browser).
    We use it to setup a database connection that can be used throughout the request.

    The variable g is globally accessible.
    """
    try:
        g.conn = engine.connect()
    except:
        print("uh oh, problem connecting to database")
        import traceback
        traceback.print_exc()
        g.conn = None


@app.teardown_request
def teardown_request(exception):
    """
    At the end of the web request, this makes sure to close the database connection.
    If you don't, the database could run out of memory!
    """
    try:
        g.conn.close()
    except Exception as e:
        pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
#
# see for routing: https://flask.palletsprojects.com/en/2.0.x/quickstart/?highlight=routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#

# @app.route('/')
# def index():
#  """
#  request is a special object that Flask provides to access web request information:
#
#  request.method:   "GET" or "POST"
#  request.form:     if the browser submitted a form, this contains the data in the form
#  request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2
#
#  See its API: https://flask.palletsprojects.com/en/2.0.x/api/?highlight=incoming%20request%20data
#
#  """

@app.route('/')
def index():
    return 'Hello World'

def object_as_dict(obj):
    return {c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs}


@app.route('/athlete', methods=['GET'])
def athlete():
    context = dict()
    Athlete = Base.classes.Athlete
    i = 0
    for row in session.query(Athlete).all():
        # print(context)
        # context.update(object_as_dict(row)) 
        context[i] = object_as_dict(row)
        i += 1
    
    # print(context)
    # athlete = session.query(Athlete).first()
    # context = object_as_dict(athlete)

    # print(response)
    # cursor = g.conn.execute("SELECT name FROM Athlete")
    # names = []
    # for result in cursor:
    #     print(result)
    #     # can also be accessed using result[0]
    #     names.append(result['name'])
    # cursor.close()

    # context = dict(data=names)
    response = app.response_class(
        response=json.dumps(context),
        mimetype='application/json'
    )
    return response


if __name__ == "__main__":
    import click

    @click.command()
    @click.option('--debug', is_flag=True)
    @click.option('--threaded', is_flag=True)
    @click.argument('HOST', default='0.0.0.0')
    @click.argument('PORT', default=8000, type=int)
    def run(debug, threaded, host, port):
        """
        This function handles command line parameters.
        Run the server using:

                python3 server.py

        Show the help text using:

                python3 server.py --help

        """

        HOST, PORT = host, port
        print("running on %s:%d" % (HOST, PORT))
        app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

    run()
