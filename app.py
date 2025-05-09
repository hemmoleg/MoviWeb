import os
from wsgiref.util import request_uri

from flask import Flask, render_template, request, url_for, redirect
from data_manager import DataManager
from models import db, User, Movie

app = Flask(__name__)

cwd = os.getcwd()
db_file = os.path.join(cwd, "data", "library.sqlite")
#app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_file}'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'

db.init_app(app)
data_manager = DataManager()


@app.route('/')
def index():
    message = request.args.get('message')
    users = data_manager.get_users()
    return render_template('index.html', users=users, message=message)


@app.route('/users')
def list_users():
    users = data_manager.get_users()
    return str(users)


@app.route('/users', methods=['POST'])
def create_user():
    name = request.form.get('name')
    data_manager.create_user(name=name)
    return redirect(url_for('index'))


@app.route('/users/<int:user_id>/movies', methods=['GET'])
def get_movies(user_id):
    message = request.args.get('message')
    user = User.query.filter_by(id=user_id).first()

    if user is None:
        return redirect(url_for('index', message=f'No user with id {user_id} in Database'))

    movies = Movie.query.filter_by(user_id=user_id).all()
    return render_template('movies.html',
                           movies=movies,
                           user_name=user.name,
                           user_id=user_id,
                           message=message)


@app.route('/users/<int:user_id>/movies', methods=['POST'])
def create_movie(user_id):
    movie_name = request.form.get('name')
    message = data_manager.add_movie(movie_name, user_id)

    if message is None:
        return redirect(url_for('get_movies', user_id=user_id))
    else:
        return redirect(url_for('get_movies', user_id=user_id, message=message))

#personal note: as it makes zero sense to have any kind of update functionality for movies
#and there were no details given on what this method is actually supposed to achive I will
#just add it for my grade's sake.
#I didn't want to ruin the visual appeal of the app by adding an update button to each movie.
#Especially when it's entirely useless. So instead I gave the img tag an onclick handler.
#However, that limited me to use GET instead of POST.
@app.route('/users/<int:user_id>/movies/<int:movie_id>/update', methods=['GET'])
def update_movie(user_id, movie_id):
    message = data_manager.update_movie(movie_id, user_id)
    if message is None:
        return redirect(url_for('get_movies', user_id=user_id))
    else:
        return redirect(url_for('get_movies', user_id=user_id, message=message))


@app.route('/users/<int:user_id>/movies/<int:movie_id>/delete', methods=['POST'])
def delete_movie(user_id, movie_id):
    message = data_manager.delete_movie(movie_id, user_id)
    return redirect(url_for('get_movies', user_id=user_id, message=message))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)

# with app.app_context():
#   db.create_all()
