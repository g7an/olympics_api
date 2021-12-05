
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
from sqlalchemy import event
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import Session
from flask import Flask, request, render_template, g, redirect, Response
from flask import json
from sqlalchemy.ext.automap import automap_base

tmpl_dir = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
app.jinja_env.filters['zip'] = zip


# class AthleteRegion(Base):
#     __table__ = 'Athlete_Region'
#     athlete_id = Column(Integer, ForeignKey('Athlete.athlete_id'), primary_key=True)
#     region_id = Column(Integer, ForeignKey('Region.region_id'), primary_key=True)



# DATABASEURI = mysql://username:password@server/db
DATABASEURI = "mysql+pymysql://21fa_yzhou193:E1hL7yOSEP@dbase.cs.jhu.edu/21fa_yzhou193_db"
# DATABASEURI = os.environ.get('DB_CONNECTION_STRING')
#
# This line creates a database engine that knows how to connect to the URI above.
#
Base = automap_base()
engine = create_engine(DATABASEURI)

# you only need to define which column is the primary key. It can automap the rest of the columns.
Table('Most_Medal',Base.metadata, Column('Event_name', VARCHAR, 
primary_key=True), autoload=True, autoload_with=engine)

Table('Gold_count',Base.metadata, Column('Name', VARCHAR, 
primary_key=True), autoload=True, autoload_with=engine)

Table('CountryCount', Base.metadata, Column('count', VARCHAR, primary_key=True), autoload=True, autoload_with=engine)

Table('Q1_Country_Gold',Base.metadata, Column('Region_name', VARCHAR, 
primary_key=True), autoload=True, autoload_with=engine)

Table('Q2_US_Gold_Athlete',Base.metadata, Column('Year', VARCHAR, 
primary_key=True), Column('Season', Integer, primary_key = True), autoload=True, autoload_with=engine)

Table('Q3_US_Excel',Base.metadata, Column('Sport_name', VARCHAR, 
primary_key=True), autoload=True, autoload_with=engine)

Table('Q5_Event_Year',Base.metadata, Column('Year', VARCHAR, 
primary_key=True), Column('Season', Integer, primary_key = True), autoload=True, autoload_with=engine)

Table('Q6_City_Game',Base.metadata, Column('City_name', VARCHAR, 
primary_key=True), autoload=True, autoload_with=engine)

Table('Q7_Partici_City',Base.metadata, Column('Year', VARCHAR, 
primary_key=True), Column('Season', Integer, primary_key = True), autoload=True, autoload_with=engine)

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
    response = app.response_class(
        response=json.dumps(context),
        mimetype='application/json'
    )
    return response

@app.route('/basic_info', methods = ['GET'])
def basic_info():
    #number of olympics games
    # print(Base.classes.keys())
    context = dict()
    Game = Base.classes.Game
    game_count = session.query(Game).count()
    context['game_count'] = game_count

    # number of events
    Event = Base.classes.Event
    event_count = session.query(Event).count()
    context['event_count'] = event_count


    # number of countries participated in year 2012
    Athlete = Base.classes.Athlete
    CountryCount = Base.classes.CountryCount

    country_count = session.query(CountryCount).first()
    context['country_count'] = object_as_dict(country_count).get('count') 

    # number of athletes
    athlete_count = session.query(Athlete).count()
    context['athlete_count'] = athlete_count

    response = app.response_class(
        response=json.dumps(context),
        mimetype='application/json'
    )   
    return response

@app.route('/male_female', methods = ['GET'])
def male_female():
    # number of male atlete
    context = dict()
    Athlete = Base.classes.Athlete
    male_count = session.query(Athlete).filter(Athlete.Gender == 'Men').count()
    context['male_count'] = male_count

    # number of female atlete
    Athlete = Base.classes.Athlete
    female_count = session.query(Athlete).filter(Athlete.Gender == 'Women').count()
    context['female_count'] = female_count

    total = (context['female_count'] + context['male_count'])
    male_ratio = context['male_count'] / total
    female_ratio = context['female_count'] / total
    context['male_ratio'] = '{:.2%}'.format(male_ratio)
    context['female_ratio'] = '{:.2%}'.format(female_ratio)

    response = app.response_class(
        response=json.dumps(context),
        mimetype='application/json'
    )   
    return response

@app.route('/event_medal', methods = ['GET'])
def event_medal():
    #return {"event_name": "swimming", "country_name": "USA", "number of medal": 15}
    context = dict()

    # country won most golden medals for each event
    Most_Medal = Base.classes.Most_Medal

    query = session.query(Most_Medal).all()
    i = 0
    for row in query:
        context[i] = object_as_dict(row)
        i += 1
    response = app.response_class(
        response=json.dumps(context),
        mimetype='application/json'
    )   
    return response

#nlp api

@app.route('/win_rate', methods = ['GET'])
def win_rate():
    #win rate of male athletes
    context = dict()
    Athlete = Base.classes.Athlete
    competitor_event = Base.classes.competitor_event
    Event = Base.classes.Event
    Medal = Base.classes.Medal
    All_male_event = session.query(Athlete).join(competitor_event,competitor_event.competitor_id == Athlete.ID).join(Event, Event.ID == competitor_event.competitor_id ).join(Medal,Medal.ID == competitor_event.medal_id).filter(Athlete.Gender == 'Men').count()
    win_event_male = session.query(Athlete).join(competitor_event,competitor_event.competitor_id == Athlete.ID).join(Event, Event.ID == competitor_event.competitor_id ).join(Medal,Medal.ID == competitor_event.medal_id).filter(Athlete.Gender == 'Men',Medal.Type == 'Gold').count()
    context['Male Win Rate'] = '{:.2%}'.format(win_event_male / All_male_event)
    
    #win rate of female athletes
    All_female_event = session.query(Athlete).join(competitor_event,competitor_event.competitor_id == Athlete.ID).join(Event, Event.ID == competitor_event.competitor_id ).join(Medal,Medal.ID == competitor_event.medal_id).filter(Athlete.Gender == 'Women').count()
    win_event_female = session.query(Athlete).join(competitor_event,competitor_event.competitor_id == Athlete.ID).join(Event, Event.ID == competitor_event.competitor_id ).join(Medal,Medal.ID == competitor_event.medal_id).filter(Athlete.Gender == 'Women',Medal.Type == 'Gold').count()
    context['Female Win Rate'] = '{:.2%}'.format(win_event_female / All_female_event)


    response = app.response_class(
        response=json.dumps(context),
        mimetype='application/json'
    )   
    return response

@app.route('/USA_info', methods = ['GET'])
def USA_info():
    #win rate of USA athletes
    context = dict()
    Athlete = Base.classes.Athlete
    competitor_event = Base.classes.competitor_event
    Event = Base.classes.Event
    Medal = Base.classes.Medal
    Region = Base.classes.Region
    Athlete_Region = Base.classes.athlete_region

    #win rate of USA athletes
    All_event = session.query(Athlete).join(competitor_event,competitor_event.competitor_id == Athlete.ID)\
        .join(Event, Event.ID == competitor_event.competitor_id ).join(Medal,Medal.ID == competitor_event.medal_id)\
            .join(Athlete_Region, Athlete_Region.athlete_id == Athlete.ID).join(Region,Region.ID == Athlete_Region.region_id).filter(Region.Region_name == 'United States').count()
    win_event = session.query(Athlete).join(competitor_event,competitor_event.competitor_id == Athlete.ID)\
        .join(Event, Event.ID == competitor_event.competitor_id ).join(Medal,Medal.ID == competitor_event.medal_id)\
            .join(Athlete_Region, Athlete_Region.athlete_id == Athlete.ID).join(Region,Region.ID == Athlete_Region.region_id).filter(Region.Region_name == 'United States',Medal.Type == 'Gold').count()
    context['US Athletes Win Rate'] = '{:.2%}'.format(win_event / All_event)

    #win rate of USA female
    All_female_event = session.query(Athlete).join(competitor_event,competitor_event.competitor_id == Athlete.ID)\
        .join(Event, Event.ID == competitor_event.competitor_id ).join(Medal,Medal.ID == competitor_event.medal_id)\
            .join(Athlete_Region, Athlete_Region.athlete_id == Athlete.ID).join(Region,Region.ID == Athlete_Region.region_id).filter(Athlete.Gender == 'Women',Region.Region_name == 'United States').count()
    win_event_female = session.query(Athlete).join(competitor_event,competitor_event.competitor_id == Athlete.ID)\
        .join(Event, Event.ID == competitor_event.competitor_id ).join(Medal,Medal.ID == competitor_event.medal_id)\
            .join(Athlete_Region, Athlete_Region.athlete_id == Athlete.ID).join(Region,Region.ID == Athlete_Region.region_id).filter(Athlete.Gender == 'Women',Region.Region_name == 'United States',Medal.Type == 'Gold').count()
    context['US Female Win Rate'] = '{:.2%}'.format(win_event_female / All_female_event)

    #win rate of USA male
    All_male_event = session.query(Athlete).join(competitor_event,competitor_event.competitor_id == Athlete.ID)\
        .join(Event, Event.ID == competitor_event.competitor_id ).join(Medal,Medal.ID == competitor_event.medal_id)\
            .join(Athlete_Region, Athlete_Region.athlete_id == Athlete.ID).join(Region,Region.ID == Athlete_Region.region_id).filter(Athlete.Gender == 'Men',Region.Region_name == 'United States').count()
    win_event_male = session.query(Athlete).join(competitor_event,competitor_event.competitor_id == Athlete.ID)\
        .join(Event, Event.ID == competitor_event.competitor_id ).join(Medal,Medal.ID == competitor_event.medal_id)\
            .join(Athlete_Region, Athlete_Region.athlete_id == Athlete.ID).join(Region,Region.ID == Athlete_Region.region_id).filter(Athlete.Gender == 'Men',Region.Region_name == 'United States',Medal.Type == 'Gold').count()
    context['US male Win Rate'] = '{:.2%}'.format(win_event_male / All_male_event)

    #medal ratio
    All_gold_count = session.query(Athlete).join(competitor_event,competitor_event.competitor_id == Athlete.ID)\
        .join(Event, Event.ID == competitor_event.competitor_id ).join(Medal,Medal.ID == competitor_event.medal_id)\
            .join(Athlete_Region, Athlete_Region.athlete_id == Athlete.ID).join(Region,Region.ID == Athlete_Region.region_id).filter(Medal.Type == 'Gold',Region.Region_name == 'United States').count()
    
    All_silver_count = session.query(Athlete).join(competitor_event,competitor_event.competitor_id == Athlete.ID)\
        .join(Event, Event.ID == competitor_event.competitor_id ).join(Medal,Medal.ID == competitor_event.medal_id)\
            .join(Athlete_Region, Athlete_Region.athlete_id == Athlete.ID).join(Region,Region.ID == Athlete_Region.region_id).filter(Medal.Type == 'Silver',Region.Region_name == 'United States').count()
    
    All_Bronze_count = session.query(Athlete).join(competitor_event,competitor_event.competitor_id == Athlete.ID)\
        .join(Event, Event.ID == competitor_event.competitor_id ).join(Medal,Medal.ID == competitor_event.medal_id)\
            .join(Athlete_Region, Athlete_Region.athlete_id == Athlete.ID).join(Region,Region.ID == Athlete_Region.region_id).filter(Medal.Type == 'Bronze',Region.Region_name == 'United States').count()
    Gold_ratio = All_gold_count / (All_gold_count + All_silver_count + All_Bronze_count)
    Silver_ratio = All_silver_count / (All_gold_count + All_silver_count + All_Bronze_count)
    Bronze_ratio = All_Bronze_count / (All_gold_count + All_silver_count + All_Bronze_count)

    context['US Gold Medal Retio:'] = '{:.2%}'.format(Gold_ratio)
    context['US Silver Medal Retio:'] = '{:.2%}'.format(Silver_ratio)
    context['US Bronze Medal Retio:'] = '{:.2%}'.format(Bronze_ratio)

    response = app.response_class(
        response=json.dumps(context),
        mimetype='application/json'
    )   
    return response

@app.route('/medal_top', methods = ['GET'])
def medal_top():
    # top 10 gold medal winner
    context = dict()
    # Athlete = Base.classes.Athlete
    # competitor_event = Base.classes.competitor_event
    # Medal = Base.classes.Medal
    # winner = session.query(Athlete).join(competitor_event,competitor_event.competitor_id == Athlete.ID)\
    #     .join(Medal,Medal.ID == competitor_event.medal_id).filter(Medal.Type == 'Gold').group_by(competitor_event.competitor_id).order_by(-func.count(competitor_event.medal_id)).all()
    Gold_count = Base.classes.Gold_count
    winner = session.query(Gold_count).all()
    i = 0
    for row in winner:
        context[i] = object_as_dict(row)
        i += 1
        if i == 10:
            break
    response = app.response_class(
        response=json.dumps(context),
        mimetype='application/json'
    )   
    return response

#Q1 Top 20 countries with the most gold medals in 120 years.
@app.route('/Gold_country', methods = ['GET'])
def Gold_country():
    Country = Base.classes.Q1_Country_Gold
    context = dict()
    ret = session.query(Country).all()
    i = 0
    for row in ret:
        context[i] = object_as_dict(row)
        i += 1
    response = app.response_class(
        response=json.dumps(context),
        mimetype='application/json'
    )   
    return response

#Q2 Total number of U.S. athletes who have won medals in previous Olympics.
@app.route('/US_Gold', methods = ['GET'])
def US_Gold():
    Top20 = Base.classes.Q2_US_Gold_Athlete
    context = dict()
    ret = session.query(Top20).all()
    i = 0
    for row in ret:
        context[i] = object_as_dict(row)
        i += 1
    response = app.response_class(
        response=json.dumps(context),
        mimetype='application/json'
    )   
    return response

#Q3 Top 10 sports U.S. athletes excel (sorted by gold medals)
@app.route('/US_excel', methods = ['GET'])
def US_excel():
    US_Excel = Base.classes.Q3_US_Excel
    context = dict()
    ret = session.query(US_Excel).all()
    i = 0
    for row in ret:
        context[i] = object_as_dict(row)
        i += 1
    response = app.response_class(
        response=json.dumps(context),
        mimetype='application/json'
    )   
    return response 

#Q5 Number of Olympic projects(events) in 120 years.
@app.route('/event_year', methods = ['GET'])
def event_year():
    event_stats = Base.classes.Q5_Event_Year
    context = dict()
    ret = session.query(event_stats).all()
    i = 0
    for row in ret:
        context[i] = object_as_dict(row)
        i += 1
    response = app.response_class(
        response=json.dumps(context),
        mimetype='application/json'
    )   
    return response 

#Q6 Find cities that have held Olympic Games (either summer or winter) for more than 1 time
@app.route('/held_cities', methods = ['GET'])
def held_cities():
    city_stats = Base.classes.Q6_City_Game
    context = dict()
    ret = session.query(city_stats).all()
    i = 0
    for row in ret:
        context[i] = object_as_dict(row)
        i += 1
    response = app.response_class(
        response=json.dumps(context),
        mimetype='application/json'
    )   
    return response 

#Q7 Find the number of countries/regions that participated in Olympic Games over the past 120 years, list out the year and the count of countries.
@app.route('/partici_cities', methods = ['GET'])
def partici_cities():
    city_stats = Base.classes.Q7_Partici_City
    context = dict()
    ret = session.query(city_stats).all()
    i = 0
    for row in ret:
        context[i] = object_as_dict(row)
        i += 1
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
