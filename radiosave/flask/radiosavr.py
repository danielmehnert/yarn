
import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash

import datetime
import sys
sys.path.append("..")
import radiosave
from radiosave import timer 

import threading

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'radiosave.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default',
    OUTPUT='../output'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv
    
    
def init_radio_db():
    db = get_db()
    with app.open_resource('radiosave_schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initradiodb')
def initdb_command():
    """Initializes the database."""
    init_radio_db()
    print 'Initialized the database.'

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db
    
    
@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

    
@app.route("/")
def show_recordings():
    db = get_db()
    cur = db.execute('select url, title from stations order by id desc')
    stations = cur.fetchall()
    
    recs = db.execute('select url, start, end from record_schedule order by id desc')
    planned = recs.fetchall()    
    stripplanned = []
    for p in planned:
        
        end = datetime.datetime.strptime(p[1].split("T")[0] + p[2], "%Y-%m-%d%H:%M")
        if end > datetime.datetime.now():
            stripplanned.append(p)
    
    recordings = os.listdir(unicode(app.config["OUTPUT"]))
    return render_template('add_recording.html', stations=stations, recordings=stripplanned, done=recordings)
    

@app.route("/addrecord", methods=['POST'])
def add_recording():
    strtime = datetime.datetime.strptime(request.form['datestart'], "%Y-%m-%dT%H:%M")
    endtimestring = request.form['datestart'].split("T")[0] + "T" + request.form['endtime']
    endtime = datetime.datetime.strptime(endtimestring, "%Y-%m-%dT%H:%M")
    if endtime > datetime.datetime.now():
        tid = request.form['urlselect'] + "_" + request.form['datestart'] + "_" + request.form['datestart'].split("T")[0] + "T" + request.form['endtime']
        set_timer(strtime, endtime, request.form['urlselect'], app.config['OUTPUT'], tid)

        db = get_db()
        db.execute('insert into record_schedule (url, start, end, status) values (?, ?, ?, ?)',
                    [request.form['urlselect'], request.form['datestart'], request.form['endtime'], tid])
        db.commit()
        flash('New record scheduled!')
    else:
        flash('Record not scheduled. Timeframe in the past.')
    return redirect(url_for('show_recordings'))

  

@app.route('/addstation', methods=['POST'])
def add_station():
    db = get_db()
    db.execute('insert into stations (url, title) values (?, ?)', [request.form['url'], request.form['title']])
    db.commit()
    flash('New station added!')
    return redirect(url_for('show_recordings'))
    
@app.route('/stations')
def station_list():
    db = get_db()
    cur = db.execute('select url, title from stations order by id desc')
    stations = cur.fetchall()
    
    return render_template('add_station.html', stations=stations)

def set_timer(starttime, endtime, streamurl, output, name):
    print name
    stop = threading.Event()
    timer_thread = threading.Thread(target=timer, name = name, args=(starttime, endtime, streamurl, output))
    timer_thread.setDaemon(True)
    timer_thread.start()
    print timer_thread.name

@app.before_first_request
def check_running_threads():
    with app.app_context():
        ts = threading.enumerate()
        print [t.name for t in ts]

"""        
def check_db_for_recordings():
    db = get_db()
        
    recs = db.execute('select url, start, end, status from record_schedule where status="" order by id desc')
    planned = recs.fetchall()
    
    for rec in planned:
        url, start, end = rec[0], rec[1], rec[2]
        now = datetime.datetime.now()
        starttime = datetime.datetime.strptime(start, "%Y-%m-%dT%H:%M")
        if starttime > now:
            print (now-starttime).seconds
            if (now-starttime).seconds < 600:
                print rec, "thread start"
            else:
                print rec, "waiting"
        
@app.before_first_request
def initialize():
    check_recordings_queue()        

def check_recordings_queue():
    with app.app_context():
        stop = threading.Event()
        query_thread = threading.Thread(target = check_db_for_recordings)
        query_thread.setDaemon(True)
        query_thread.start()
        query_thread.join(10*60)
        
        if query_thread.is_alive():
            stop.set()

"""

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=0)
