import json

import requests

from models import db, User, Movie

class DataManager():
    def create_user(self, name):
        new_user = User(name=name)
        db.session.add(new_user)
        self.db_commit()


    def get_users(self):
        return User.query.all()


    def get_movies(self, user_id):
        return Movie.query.get(user_id=user_id)


    def add_movie(self, title, user_id):
        response = requests.post(f"https://www.omdbapi.com/?apikey=9d3237b8&t={title}")

        response = json.loads(response.text)
        if response["Response"] == "False":
            return "Movie not found in OMDb"

        new_movie = Movie(name=title, director=response["Director"],
                          year=response["Year"], poster_url=response["Poster"],
                          user_id=user_id)

        db.session.add(new_movie)
        self.db_commit()


    def update_movie(self, movie_id, user_id):
        movie = Movie.query.filter_by(id=movie_id, user_id=user_id).first()
        if movie is None:
            return f"No movie found with ID {movie_id}"

        try:
            response = requests.post(f"https://www.omdbapi.com/?apikey=9d3237b8&t={movie.name}")
        except ConnectionError:
            return "No connection to API!"

        data = response.json()

        if data.get("Response") == "False":
            return f"Movie “{movie.name}” not found in OMDb"

        movie.director = data.get("Director", movie.director)
        movie.year = data.get("Year", movie.year)
        movie.poster_url = data.get("Poster", movie.poster_url)

        self.db_commit()

        return None


    def change_movie_title(self, movie_id, new_title):
        movie = Movie.query.get(movie_id)
        movie.name = new_title
        self.db_commit()


    def delete_movie(self, movie_id, user_id):
        movie = Movie.query.filter_by(id=movie_id, user_id=user_id).first()
        db.session.delete(movie)
        self.db_commit()


    def db_commit(self):
        try:
            db.session.commit()
        except Exception as e:
            return f'Error writing to Database. {e}'