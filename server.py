

"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os, secrets, hashlib
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, session, flash
from flask_login import login_required, current_user;

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

#Secret key is needed for sessions
sk = secrets.token_hex(256);
app.config['SECRET_KEY'] = sk;


#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@34.73.36.248/project1
#
# For example, if you had username zy2431 and password 123123, then the following line would be:
#
#     DATABASEURI = "postgresql://zy2431:123123@34.73.36.248/project1"
#
# Modify these with your own credentials you received from TA!
DATABASE_USERNAME = "fl2627"
DATABASE_PASSWRD = "4151"
DATABASE_HOST = "34.148.107.47" # change to 34.28.53.86 if you used database 2 for part 2
DATABASEURI = f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWRD}@{DATABASE_HOST}/project1"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
with engine.connect() as conn:
	create_table_command = """
	CREATE TABLE IF NOT EXISTS test (
		id serial,
		name text
	)
	"""
	res = conn.execute(text(create_table_command))
	insert_table_command = """INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace')"""
	res = conn.execute(text(insert_table_command))
	# you need to commit for create, insert, update queries to reflect
	conn.commit()

metadata = MetaData();
users = Table(
    'users',
    metadata,
    Column('username', String, primary_key = True),
    Column('salt', String),
    Column('pw', String),
)

user_liked_game = Table(
    'user_liked_game',
    metadata,
    Column('username', String, primary_key = True),
    Column('game_id', String, primary_key = True),
)

user_disliked_game = Table(
    'user_disliked_game',
    metadata,
    Column('username', String, primary_key = True),
    Column('game_id', String, primary_key = True),
)

games = Table(
    'game',
    metadata,
    Column('game_id', String, primary_key = True),
    Column('name', String, nullable=False),
    Column('release_date', Date),
    Column('description', String),
    Column('type', String, nullable=False),
    Column('media_rating', Float),
    Column('price', Float),
    Column('age_restriction', Integer),
)

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
		import traceback; traceback.print_exc()
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
# see for routing: https://flask.palletsprojects.com/en/1.1.x/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
	"""
	request is a special object that Flask provides to access web request information:

	request.method:   "GET" or "POST"
	request.form:     if the browser submitted a form, this contains the data in the form
	request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

	See its API: https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data
	"""

	# DEBUG: this is debugging code to see what request looks like
	print(request.args)


	#
	# example of a database query
	#
	select_query = "SELECT name from test"
	cursor = g.conn.execute(text(select_query))
	names = []
	for result in cursor:
		names.append(result[0])
	cursor.close()

	#
	# Flask uses Jinja templates, which is an extension to HTML where you can
	# pass data to a template and dynamically generate HTML based on the data
	# (you can think of it as simple PHP)
	# documentation: https://realpython.com/primer-on-jinja-templating/
	#
	# You can see an example template in templates/index.html
	#
	# context are the variables that are passed to the template.
	# for example, "data" key in the context variable defined below will be 
	# accessible as a variable in index.html:
	#
	#     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
	#     <div>{{data}}</div>
	#     
	#     # creates a <div> tag for each element in data
	#     # will print: 
	#     #
	#     #   <div>grace hopper</div>
	#     #   <div>alan turing</div>
	#     #   <div>ada lovelace</div>
	#     #
	#     {% for n in data %}
	#     <div>{{n}}</div>
	#     {% endfor %}
	#
	context = dict(data = names)


	#
	# render_template looks in the templates/ folder for files.
	# for example, the below file reads template/index.html
	#
	return render_template("index.html", **context)



@app.route('/search', methods=['POST'])
def search():
#accessing search content
    search_text = request.form['search_text']
    search_text_special = '%'+search_text+'%'
    res = g.conn.execute(text("select name, date(release_date), price ,media_rating, age_restriction, game_dev.developer_name, Game.game_id from Game natural join game_genre inner join game_dev on Game.game_id = game_dev.game_id inner join game_pub on game.game_id = game_pub.game_id where name ilike :e1 or genre_name ilike :e2 group by Game.game_id, name, release_date, price ,media_rating, age_restriction, game_dev.developer_name"),{'e1':search_text_special, 'e2':search_text_special})
    #res = g.conn.execute(text(sql_search_text), [(search_text_special,)])
    game_res = []
    for game in res:
        print(game)
        if (session.get('username') is not None):
            tmp = g.conn.execute(text("select * from user_disliked_game where game_id = :gid and username like :usn"),
                    {'gid': game[6], 'usn':session.get('username')}).fetchone();
            if tmp is None:
                game_res.append(game);
        else:
            game_res.append(game)

    #Pull a list of liked games
    lkg = [];
    query = g.conn.execute(text("select game_id from user_liked_game where username like :usn"),
            {'usn':session.get('username')});
    for i in query:
        lkg.append(i[0]);

    print(lkg);
    return render_template("index.html",game_res = game_res, search_text = search_text, liked_games = lkg, logged_in = (session.get('username') is not None));

# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
	# accessing form inputs from user
	name = request.form['name']
	
	# passing params in for each variable into query
	params = {}
	params["new_name"] = name
	g.conn.execute(text('INSERT INTO test(name) VALUES (:new_name)'), params)
	g.conn.commit()
	return redirect('/')


#Login code template is learnt from https://flask-login.readthedocs.io/en/latest/
@app.route('/login',methods=['GET','POST'])
def login():
    if session.get('username') is not None:
        print("Already logged in");
        return redirect("profile");
    if request.method == 'POST':
        print(session);
        print('User is trying to login.');
        username = request.form['username'];
        password = request.form['password'];
        response = None;
        auth = False;
        fetched_user = g.conn.execute(text('select * from users where username = :usn'),
                {'usn':username}).fetchone();
        if fetched_user is not None:
            salt = fetched_user[1];
            salted = password + salt;
            hashed = hashlib.sha256(salted.encode()).hexdigest();
            if (hashed == fetched_user[2]):
                auth = True;

        #incorrect login info
        if fetched_user is None or (not auth):
            print('No such user');
            response = "Invalid username or password";
            flash(response, 'error');
            return redirect("login");
        else:
            print("User authenticated");
            session.clear();
            session['username'] = username;
            return redirect("profile");


    return render_template("login.html");

#Display profile, serve as a sanity check for session
#reference: https://www.digitalocean.com/community/tutorials/how-to-add-authentication-to-your-app-with-flask-login
@app.route('/profile', methods=['GET'])
def profile():
    if session.get('username') is None:
        flash("You have not logged in", 'error');
        return redirect("info");
    else:
        return render_template('profile.html', name = session['username']);

@app.route('/logout', methods=['GET'])
def logout():
    if session.get('username') is None:
        return redirect('login');
    else:
        session.clear();
        flash("Successfully logged out!");
        return redirect("login");

@app.route('/register', methods=['GET','POST'])
def register():
    if session.get('username') is None and request.method == 'GET':
        return render_template('register.html');
    elif session.get('username') is not None:
        flash("You have to logout before register.", 'error');
        return redirect("info");
    else:
        print("User is trying to register.");
        username = request.form['username'];
        password = request.form['password'];
        rpw = request.form['rpw'];

        #check if username input is too long.
        if len(username) > 20:
            flash('Username exceeds 20 character!', 'error');
            return render_template('register.html');

        if len(password) <= 5:
            flash('Passowrd must contain more than 5 characters.', 'error');
            return render_template('register.html', username = username);

        username_check = g.conn.execute(text('select * from users where username = :usn'),
                {'usn':username}).fetchone();
        print(username_check);
        if username_check is not None:
            flash("Username already taken",'error');
            return render_template('register.html');
        if password != rpw:
            flash("Password does not match",'error');
            return render_template('register.html', username = username);

        salt = secrets.token_hex(8)
        salted = password + salt;
        hashed = hashlib.sha256(salted.encode()).hexdigest();
        stmt = insert(users).values(username = username, salt = salt, pw = hashed);
        print(stmt);
        g.conn.execute(stmt);
        g.conn.commit();
        flash('Successfully registered');
        return redirect('login');
    
@app.route('/info', methods=['GET'])
def info():
    return render_template('info.html');

@app.route('/liked-games', methods=['GET'])
def game_liked():
    if session.get('username') is None:
        flash('You have not logged in.', 'error');
        return redirect('info');
    else:
        fetched_games = g.conn.execute(text('select game_id from user_liked_game where username = :usn'),
                {'usn' : session.get('username')}).fetchone();
        if fetched_games is None:
            return render_template('liked-games.html', username = session.get('username'), games_liked = None);
        else:
            fetched_games = g.conn.execute(text('select game_id from user_liked_game where username = :usn'),
                    {'usn' : session.get('username')});

            raw_list = [i for i in fetched_games];
            lst = [];
            for r in raw_list:
                game_info = g.conn.execute(text('select game_id, name, Date(release_date) from game where game_id = :gid'),
                        {'gid' : r[0]}).fetchone();
                tmp = [game_info[0], game_info[1], game_info[2]];
                lst.append(tmp);

            return render_template('liked-games.html', username = session.get('username'), games_liked = lst);

@app.route('/unlike/<id>', methods=['POST'])
def unlike(id):
    if session.get('username') is None:
        flash('You have not logged in.', 'error');
        return redirect('../info');
    else:
        stmt = user_liked_game.delete().where(user_liked_game.c.username == session.get('username')).where(user_liked_game.c.game_id == id);
        g.conn.execute(stmt);
        g.conn.commit();
        return redirect('../liked-games');


@app.route('/disliked-games', methods=['GET'])
def game_disliked():
    if session.get('username') is None:
        flash('You have not logged in.', 'error');
        return redirect('info');
    else:
        fetched_games = g.conn.execute(text('select game_id from user_disliked_game where username = :usn'),
                {'usn' : session.get('username')}).fetchone();
        if fetched_games is None:
            return render_template('disliked-games.html', username = session.get('username'), games_disliked = None);
        else:
            fetched_games = g.conn.execute(text('select game_id from user_disliked_game where username = :usn'),
                    {'usn' : session.get('username')});

            raw_list = [i for i in fetched_games];
            lst = [];
            for r in raw_list:
                game_info = g.conn.execute(text('select game_id, name, Date(release_date) from game where game_id = :gid'),
                        {'gid' : r[0]}).fetchone();
                tmp = [game_info[0], game_info[1], game_info[2]];
                lst.append(tmp);

            return render_template('disliked-games.html', username = session.get('username'), games_disliked = lst);

@app.route('/remove/<id>', methods=['POST'])
def remove(id):
    if session.get('username') is None:
        flash('You have not logged in.', 'error');
        return redirect('../info');
    else:
        stmt = user_disliked_game.delete().where(user_disliked_game.c.username == session.get('username')).where(user_disliked_game.c.game_id == id);
        g.conn.execute(stmt);
        g.conn.commit();
        return redirect('../disliked-games');

@app.route('/like/<id>', methods=['POST'])
def like(id):
    if session.get('username') is None:
        flash('You have not logged in.', 'error');
        return redirect('../info');
    else:
        stmt = insert(user_liked_game).values(username = session.get('username'), game_id = id);
        g.conn.execute(stmt);
        g.conn.commit();
        return redirect('../liked-games');

@app.route('/dislike/<id>', methods=['POST'])
def dislike(id):
    if session.get('username') is None:
        flash('You have not logged in.', 'error');
        return redirect('../info');
    else:
        stmt = insert(user_disliked_game).values(username = session.get('username'), game_id = id);
        g.conn.execute(stmt);
        g.conn.commit();
        return redirect('../disliked-games');


@app.route('/delete', methods=['GET', 'POST'])
def delete():
    if session.get('username') is None:
        flash('You have not logged in.', 'error');
        return redirect('info');

    if request.method == 'GET':
        return render_template('delete.html', current_user = session.get('username'));
    elif request.method == 'POST':
        confirmation = (request.form.get('confirm-deletion') == 'on');
        if not confirmation:
            flash('You have to click the confirm checkbox', 'error');
            return render_template('delete.html', current_user = session.get('username'));
        password = request.form['password'];
        auth = False;
        fetched_user = g.conn.execute(text('select * from users where username = :usn'),
                {'usn':session.get('username')}).fetchone();
        salt = None;
        pw = None;
        if fetched_user is not None:
            salt = fetched_user[1];
            salted = password + salt;
            hashed = hashlib.sha256(salted.encode()).hexdigest();
            if (hashed == fetched_user[2]):
                auth = True;
        else:
            print('major exception');
            flash('Failure', 'error');
            session.clear();
            return redirect('login');
        
        if auth:
            #Begin deletion.
            stmt = users.delete().where(users.c.username == session.get('username'));
            print(stmt);
            g.conn.execute(stmt);
            g.conn.commit();
            session.clear();
            flash('Account deleted.');
            return redirect('info');
        else:
            flash('Incorrect password', 'error');
            return render_template('delete.html', current_user = session.get('username'));



if __name__ == "__main__":
	import click

	@click.command()
	@click.option('--debug', is_flag=True)
	@click.option('--threaded', is_flag=True)
	@click.argument('HOST', default='0.0.0.0')
	@click.argument('PORT', default=8111, type=int)
	def run(debug, threaded, host, port):
		"""
		This function handles command line parameters.
		Run the server using:

			python server.py

		Show the help text using:

			python server.py --help

		"""

		HOST, PORT = host, port
		print("running on %s:%d" % (HOST, PORT))
		app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

run()
