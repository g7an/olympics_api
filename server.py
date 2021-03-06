
"""
To run locally:
        python server.py
Go to http://localhost:8000 in your browser.
"""

import os
# accessible as a variable in index.html
from collections import defaultdict
from sqlalchemy import *
from sqlalchemy import event
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import Session
from flask import Flask, request, g
from flask import json
from sqlalchemy.ext.automap import automap_base
from flask_cors import CORS

tmpl_dir = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
app.jinja_env.filters['zip'] = zip

# add cross origin support
app.config['CORS_HEADERS'] = 'Content-Type'

CORS(app)



# DATABASEURI = mysql://username:password@server/db
DATABASEURI = os.environ.get('DB_CONNECTION_STRING')

#
# This line creates a database engine that knows how to connect to the URI above.
#
Base = automap_base()
engine = create_engine(DATABASEURI)

# you only need to define which column is the primary key. It can automap the rest of the columns.
Table('Most_Medal', Base.metadata, Column('Event_name', VARCHAR, 
primary_key=True), autoload=True, autoload_with=engine)

Table('Gold_count', Base.metadata, Column('Name', VARCHAR, 
primary_key=True), autoload=True, autoload_with=engine)

Table('CountryCount', Base.metadata, Column('count', VARCHAR, primary_key=True), autoload=True, autoload_with=engine)



Table('Q1_Country_Gold',Base.metadata, Column('Region_name', VARCHAR, 
primary_key=True), autoload=True, autoload_with=engine)

Table('Q2_US_Gold_Athlete',Base.metadata, Column('Year', VARCHAR, 
primary_key=True), Column('Season', Integer, primary_key = True), autoload=True, autoload_with=engine)

Table('All_Excel',Base.metadata, Column('Region_name', VARCHAR, primary_key = True), Column('Sport_name', VARCHAR, 
primary_key=True), autoload=True, autoload_with=engine)

Table('Q5_Event_Year',Base.metadata, Column('Year', VARCHAR, 
primary_key=True), Column('Season', VARCHAR, primary_key = True), autoload=True, autoload_with=engine)

Table('Q6_City_Game',Base.metadata, Column('City_name', VARCHAR, 
primary_key=True), autoload=True, autoload_with=engine)

Table('Q7_Partici_City',Base.metadata, Column('Year', VARCHAR, 
primary_key=True), Column('Season', VARCHAR, primary_key = True), autoload=True, autoload_with=engine)

# reflect the tables
Base.prepare(engine, reflect=True)

session = Session(engine)


@app.before_request
def before_request():
    """
    This function is run at the beginning of every web request 
    (every time entering an address in the web browser).
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
    Otherwise, the database could run out of memory
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

# helper function to convert sqlalchemy object into a dictionary
def object_as_dict(obj):
    return {c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs}


@app.route('/region', methods=['GET'])
def region():
    """
    This function responds to a request for /region, 
    with all the region info in the database
    """
    Region = Base.classes.region
    context = {
        i: object_as_dict(row)
        for i, row in enumerate(session.query(Region).all())
    }

    return app.response_class(
        response=json.dumps(context),
        mimetype='application/json'
    )

@app.route('/basic_info', methods = ['GET'])
def basic_info():
    """
    This function responds to a request for /basic_info, with data including:
    1. The number of athletes in total
    2. The number of regions attended the olympic game (in 2012)
    3. The number of events in total (up to 2014)
    4. The number of games held (up to 2014)
    """

    #number of olympics games
    # print(Base.classes.keys())
    context = {}
    Game = Base.classes.game
    game_count = session.query(Game).count()
    context['game_count'] = game_count

    # number of events
    Event = Base.classes.event
    event_count = session.query(Event).count()
    context['event_count'] = event_count


    # number of countries participated in year 2012
    Athlete = Base.classes.athlete
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
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/male_female', methods = ['GET'])
def male_female():
    """
    This function responds to a request for /male_female,
    with data including the number of male and female athlete,
    and the percentage of male and female athlete
    """
    # number of male atlete
    context = {}
    Athlete = Base.classes.athlete
    male_count = session.query(Athlete).filter(Athlete.Gender == 'Men').count()
    context['male_count'] = male_count

    # number of female atlete
    female_count = session.query(Athlete).filter(Athlete.Gender == 'Women').count()
    context['female_count'] = female_count

    total = (context['female_count'] + context['male_count'])
    male_ratio = context['male_count'] / total
    female_ratio = context['female_count'] / total
    context['male_ratio'] = '{:.2%}'.format(male_ratio)
    context['female_ratio'] = '{:.2%}'.format(female_ratio)

    return app.response_class(
        response=json.dumps(context),
        mimetype='application/json'
    )

@app.route('/event_medal', methods = ['GET'])
def event_medal():
    """
    This function responds to a request for /event_medal,
    with data including the event name, 
    the country/region that earned the most medal,
    and the number of medals they earned
    """
    # country won most golden medals for each event
    Most_Medal = Base.classes.Most_Medal

    query = session.query(Most_Medal).all()
    context = {i: object_as_dict(row) for i, row in enumerate(query)}

    return app.response_class(
        response=json.dumps(context),
        mimetype='application/json'
    )


@app.route('/win_rate', methods = ['GET'])
def win_rate():
    """
    This function responds to a request for /win_rate,
    with data including the chance (in percentage) that a male athlete wins a game,
    and the chance (in percentage) that a female athlete wins a game
    """

    #win rate of male athletes
    context = {}
    Athlete = Base.classes.athlete
    competitor_event = Base.classes.competitor_event
    Event = Base.classes.event
    Medal = Base.classes.medal
    All_male_event = session.query(Athlete).join(competitor_event,competitor_event.competitor_id == Athlete.ID).join(Event, Event.ID == competitor_event.competitor_id ).join(Medal,Medal.ID == competitor_event.medal_id).filter(Athlete.Gender == 'Men').count()
    win_event_male = session.query(Athlete).join(competitor_event,competitor_event.competitor_id == Athlete.ID).join(Event, Event.ID == competitor_event.competitor_id ).join(Medal,Medal.ID == competitor_event.medal_id).filter(Athlete.Gender == 'Men',Medal.Type == 'Gold').count()
    context['Male Win Rate'] = '{:.2%}'.format(win_event_male / All_male_event)

    #win rate of female athletes
    All_female_event = session.query(Athlete).join(competitor_event,competitor_event.competitor_id == Athlete.ID).join(Event, Event.ID == competitor_event.competitor_id ).join(Medal,Medal.ID == competitor_event.medal_id).filter(Athlete.Gender == 'Women').count()
    win_event_female = session.query(Athlete).join(competitor_event,competitor_event.competitor_id == Athlete.ID).join(Event, Event.ID == competitor_event.competitor_id ).join(Medal,Medal.ID == competitor_event.medal_id).filter(Athlete.Gender == 'Women',Medal.Type == 'Gold').count()
    context['Female Win Rate'] = '{:.2%}'.format(win_event_female / All_female_event)


    return app.response_class(
        response=json.dumps(context),
        mimetype='application/json'
    )

@app.route('/compete_info', methods = ['GET'])
def compete_info():
    """""
    This function responds to a request for /compete_info,
    with data including the chance (in percentage) that an athlete from a country (query parameter) wins a game,
    the chance (in percentage) that a male/female athlete from a country (query parameter) wins a game,
    the chance (in percentage) that an athlete wins a gold/silver/bronze medal
    """
    region_name = request.args['region']
    #win rate of athletes
    context = {}
    Athlete = Base.classes.athlete
    competitor_event = Base.classes.competitor_event
    Event = Base.classes.event
    Medal = Base.classes.medal
    Region = Base.classes.region
    Athlete_Region = Base.classes.athlete_region

    #win rate of athletes
    All_event = session.query(Athlete).join(competitor_event,competitor_event.competitor_id == Athlete.ID)\
        .join(Event, Event.ID == competitor_event.event_id ).join(Medal,Medal.ID == competitor_event.medal_id)\
            .join(Athlete_Region, Athlete_Region.athlete_id == Athlete.ID).join(Region,Region.ID == Athlete_Region.region_id).filter(Region.Region_name == region_name).count()

    win_event = session.query(Athlete).join(competitor_event,competitor_event.competitor_id == Athlete.ID)\
        .join(Event, Event.ID == competitor_event.event_id ).join(Medal,Medal.ID == competitor_event.medal_id)\
            .join(Athlete_Region, Athlete_Region.athlete_id == Athlete.ID).join(Region,Region.ID == Athlete_Region.region_id).filter(Region.Region_name == region_name,Medal.Type == 'Gold').count()

    if All_event == 0:
        context['win_rate'] = 'N/A'
    else:
        context['win_rate'] = '{:.2%}'.format(win_event / All_event)

    #win rate of female
    All_female_event = session.query(Athlete).join(competitor_event,competitor_event.competitor_id == Athlete.ID)\
        .join(Event, Event.ID == competitor_event.event_id ).join(Medal,Medal.ID == competitor_event.medal_id)\
            .join(Athlete_Region, Athlete_Region.athlete_id == Athlete.ID).join(Region,Region.ID == Athlete_Region.region_id).filter(Athlete.Gender == 'Women',Region.Region_name == region_name).count()
    win_event_female = session.query(Athlete).join(competitor_event,competitor_event.competitor_id == Athlete.ID)\
        .join(Event, Event.ID == competitor_event.event_id ).join(Medal,Medal.ID == competitor_event.medal_id)\
            .join(Athlete_Region, Athlete_Region.athlete_id == Athlete.ID).join(Region,Region.ID == Athlete_Region.region_id).filter(Athlete.Gender == 'Women',Region.Region_name == region_name,Medal.Type == 'Gold').count()

    if All_female_event == 0:
        context['female_rate'] = 'N/A'
    else:
        context['female_rate'] = '{:.2%}'.format(win_event_female / All_female_event)

    #win rate of male
    All_male_event = session.query(Athlete).join(competitor_event,competitor_event.competitor_id == Athlete.ID)\
        .join(Event, Event.ID == competitor_event.event_id ).join(Medal,Medal.ID == competitor_event.medal_id)\
            .join(Athlete_Region, Athlete_Region.athlete_id == Athlete.ID).join(Region,Region.ID == Athlete_Region.region_id).filter(Athlete.Gender == 'Men',Region.Region_name == region_name).count()
    win_event_male = session.query(Athlete).join(competitor_event,competitor_event.competitor_id == Athlete.ID)\
        .join(Event, Event.ID == competitor_event.event_id ).join(Medal,Medal.ID == competitor_event.medal_id)\
            .join(Athlete_Region, Athlete_Region.athlete_id == Athlete.ID).join(Region,Region.ID == Athlete_Region.region_id).filter(Athlete.Gender == 'Men',Region.Region_name == region_name,Medal.Type == 'Gold').count()

    if All_male_event == 0:
        context['male_rate'] = 'N/A'
    else:
        context['male_rate'] = '{:.2%}'.format(win_event_male / All_male_event)

    #medal ratio
    All_gold_count = session.query(Athlete).join(competitor_event,competitor_event.competitor_id == Athlete.ID)\
        .join(Event, Event.ID == competitor_event.event_id ).join(Medal,Medal.ID == competitor_event.medal_id)\
            .join(Athlete_Region, Athlete_Region.athlete_id == Athlete.ID).join(Region,Region.ID == Athlete_Region.region_id).filter(Medal.Type == 'Gold',Region.Region_name == region_name).count()

    All_silver_count = session.query(Athlete).join(competitor_event,competitor_event.competitor_id == Athlete.ID)\
        .join(Event, Event.ID == competitor_event.event_id ).join(Medal,Medal.ID == competitor_event.medal_id)\
            .join(Athlete_Region, Athlete_Region.athlete_id == Athlete.ID).join(Region,Region.ID == Athlete_Region.region_id).filter(Medal.Type == 'Silver',Region.Region_name == region_name).count()

    All_Bronze_count = session.query(Athlete).join(competitor_event,competitor_event.competitor_id == Athlete.ID)\
        .join(Event, Event.ID == competitor_event.event_id ).join(Medal,Medal.ID == competitor_event.medal_id)\
            .join(Athlete_Region, Athlete_Region.athlete_id == Athlete.ID).join(Region,Region.ID == Athlete_Region.region_id).filter(Medal.Type == 'Bronze',Region.Region_name == region_name).count()


    if All_gold_count + All_silver_count + All_Bronze_count != 0:
        context['gold_rate'] = '{:.2%}'.format(All_gold_count / (All_gold_count + All_silver_count + All_Bronze_count))
        context['silver_rate'] = '{:.2%}'.format(All_silver_count / (All_gold_count + All_silver_count + All_Bronze_count))
        context['bronze_rate'] = '{:.2%}'.format(All_Bronze_count / (All_gold_count + All_silver_count + All_Bronze_count))
    else:
        context['gold_rate'] = 'N/A'
        context['silver_rate'] = 'N/A'
        context['bronze_rate'] = 'N/A'

    return app.response_class(
        response=json.dumps(context),
        mimetype='application/json'
    )


@app.route('/medal_top', methods = ['GET'])
def medal_top():
    """
    This function responds to a request for /medal_top
    with the name of top 10 gold medal winner and the number of medals they win
    """
    context = {}
    Gold_count = Base.classes.Gold_count
    winner = session.query(Gold_count).all()
    i = 0
    for row in winner:
        context[i] = object_as_dict(row)
        i += 1
        if i == 10:
            break
    return app.response_class(
        response=json.dumps(context),
        mimetype='application/json'
    )


@app.route('/gold_country', methods = ['GET'])
def Gold_country():
    """
    This function responds to a request for /gold_country
    with top 20 countries with the most gold medals in 120 years. 
    """
    Country = Base.classes.Q1_Country_Gold
    ret = session.query(Country).all()
    context = {i: object_as_dict(row) for i, row in enumerate(ret)}
    return app.response_class(
        response=json.dumps(context),
        mimetype='application/json'
    )

@app.route('/US_Gold', methods = ['GET'])
def US_Gold():
    """
    This function responds to a request for /US_Gold
    with total number of U.S. athletes who have won medals in previous Olympics.
    """

    Top20 = Base.classes.Q2_US_Gold_Athlete
    ret = session.query(Top20).all()
    context = {i: object_as_dict(row) for i, row in enumerate(ret)}
    return app.response_class(
        response=json.dumps(context),
        mimetype='application/json'
    )

#Q3 Top 10 sports all countries athletes excel (sorted by gold medals)
@app.route('/country_excel', methods = ['GET'])
def country_excel():
    """
    This function responds to a request for /country_excel
    with top 10 sports all countries athletes excel (sorted by gold medals)
    """
    all_excel = Base.classes.All_Excel
    context = {}
    ret = session.query(all_excel).all()
    i = 0
    country_count = defaultdict(int)
    for row in ret:
        row = object_as_dict(row)
        if country_count[str(row['Region_name'])] == 10:
            continue
        context[i] = row
        i += 1
        country_count[str(row['Region_name'])] += 1
        
    return app.response_class(
        response=json.dumps(context),
        mimetype='application/json'
    ) 


@app.route('/event_year', methods = ['GET'])
def event_year():
    """
    This function responds to a request for /event_year
    with number of Olympic events in 120 years
    """
    event_stats = Base.classes.Q5_Event_Year
    ret = session.query(event_stats).all()
    context = {i: object_as_dict(row) for i, row in enumerate(ret)}
    return app.response_class(
        response=json.dumps(context),
        mimetype='application/json'
    ) 


@app.route('/held_cities', methods = ['GET'])
def held_cities():
    """
    This function responds to a request for /held_cities
    with cities that have held Olympic Games (either summer or winter) for more than 1 time
    """
    city_stats = Base.classes.Q6_City_Game
    ret = session.query(city_stats).all()
    context = {i: object_as_dict(row) for i, row in enumerate(ret)}
    return app.response_class(
        response=json.dumps(context),
        mimetype='application/json'
    ) 

@app.route('/partici_cities', methods = ['GET'])
def partici_cities():
    """
    This function responds to a request for /partici_cities
    with number of countries/regions that participated in Olympic Games over the past 120 years,
    listing out the year and the count of countries.
    """
    city_stats = Base.classes.Q7_Partici_City
    ret = session.query(city_stats).all()
    context = {i: object_as_dict(row) for i, row in enumerate(ret)}
    return app.response_class(
        response=json.dumps(context),
        mimetype='application/json'
    )

@app.route('/nlp', methods = ['GET'])
def nlp_api():
    """
    This function responds to a request for /nlp.
    It passes the user input to ln2sql, and passes the sql query generates by ln2sql to the database.
    It returns the result of the query.
    """

    user_input = request.args['user_input']

    # pass the user input to the ln2sql model, and get the query if possible
    command = "python -m ln2sql.ln2sql.main -d database_store/olympics.sql -l lang_store/english.csv -j output.json -i '"+ user_input +"'"
    os.system(command)

    context = {}

    if os.path.exists('output.txt'):
        # read the query from the output.txt file
        data = []
        with open('output.txt', 'r',encoding='utf8') as f:
            for i in f:
                data.append([j for j in i.split()])
        stmt = ''
        for i in data:
            if not i:
                continue
            for c in i:
                stmt+= c + ' '
        if "OOV" not in stmt:
            cursor = engine.execute(text(stmt))

            i=0
            for result in cursor:
                cur = {k: v for k, v in result._mapping.items()}
                context[i] = cur
                i += 1
        else:
            context[0] = "Wrong input"


        os.system('rm output.txt')

    return app.response_class(
            response=json.dumps(context),
            mimetype='application/json'
    )


if __name__ == "__main__":
    import click
    import sys
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
        import os
        HOST, PORT = host, port
        print("running on %s:%d" % (HOST, PORT))
        app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

    run()

