import os
import sqlite3
from flask import Flask , request, render_template, g, session, abort, flash

#Create Flask instance and pass module
app = Flask(__name__)
app.config.from_object(__name__)

#Config ENV variables

app.config.update(dict(
    DATABASE = os.path.join(app.root_path, 'flaskr.db'),
    SECURITY_KEY = 'development_key',
    USERNAME = 'admin',
    PASSWORD = 'admin'
))

app.config.from_envvar('FLASK_SETTINGS', silent=True)

def connect_db():
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return  rv

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    init_db()
    print 'Initialized the database'


#Create function to sustain open DB connection
def get_db():
    if not hasattr(g,'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

#def function to end connection

@app.teardown_appcontext
def close_db(error):
    if hasattr(g,'sqlite_db'):
        g.sqlite_db.close()

@app.route('/')
def show_entries():
    db = get_db()
    cur = db.execute('select title, text from entries order by id desc')
    entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries)

@app.route('/add', methods = ['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('insert into entries (title, text) values (?,?)', [request.form['title'], request.form['text']])
    db.commit()
    flash('New entry success')
    return render_template('/')

@app.route('/login', methods = ['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('Logged in')
            return render_template('/')
    return render_template('login.html', error = error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('Logged out')
    return render_template('/')




