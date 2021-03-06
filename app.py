import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from models import setup_db, Actor, Movie
from auth import AuthError, requires_auth


def create_app(test_config=None):

    # create and configure the app

    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PATCH,POST,DELETE,OPTIONS')

        return response

    # ACTORS ENDPOINTS

    @app.route('/actors')
    def get_actors():
        # returning all the actors in the database
        actors = Actor.query.all()
        # if mo record exist abort with NOt Found error
        if len(actors) == 0:
            abort(404)

        return jsonify({'success': True, 'actors':
                       [actor.format() for actor in actors]})

    @app.route('/actors/<int:actor_id>', methods=['DELETE'])
    @requires_auth('delete:actor')
    def delete_actor(jwt, actor_id):
        # retrieve the specifc record
        actor = Actor.query.get(actor_id)
        # if not exist, abort with not found
        if actor is None:
            abort(404)

        # delete it, if exist
        actor.delete()

        return jsonify({'success': True, 'actor_id': actor_id})

    @app.route('/actors', methods=['POST'])
    @requires_auth('post:actor')
    def create_actor(jwt):
        # insert new actor record in the database
        data = request.get_json()

        # if data in the reqiest missing, abort
        if ('name' not in data or
                'age' not in data or
                'gender' not in data):
            abort(400)

        # insert
        actor = Actor(name=data['name'],
                      gender=data['gender'],
                      age=data['age'])
        actor.insert()

        return jsonify({'success': True,
                        'actor': actor.format(),
                        'actor_id': actor.id})

    @app.route('/actors/<int:actor_id>', methods=['PATCH'])
    @requires_auth('patch:actor')
    def edit_actor(jwt, actor_id):
        # modify existing actor
        data = request.get_json()

        # retrieve it first
        actor = Actor.query.get(actor_id)

        # abort of not exist
        if actor is None:
            abort(404)

        # checking which property to change
        if 'name' in data:
            actor.name = data['name']

        if 'gender' in data:
            actor.gender = data['gender']

        if 'age' in data:
            actor.age = data['age']

        # after changing, update in the database
        actor.update()

        return jsonify({'success': True,
                        'actor': actor.format(),
                        'actor_id': actor_id})

    # MOVIES ENDPOINTS

    @app.route('/movies')
    def get_movies():
        # retrieve all movies in the database
        movies = Movie.query.all()

        # if no record, abort with not found error
        if len(movies) == 0:
            abort(404)

        return jsonify({'success': True,
                       'movies': [movie.format() for movie in movies]})

    @app.route('/movies/<int:movie_id>', methods=['DELETE'])
    @requires_auth('delete:movie')
    def delete_movie(jwt, movie_id):
        # remove specific movie as permited user request
        movie = Movie.query.get(movie_id)

        # check if its exist
        if movie is None:
            abort(404)

        # successfully remove it
        movie.delete()

        return jsonify({'success': True, 'movie_id': movie_id})

    @app.route('/movies', methods=['POST'])
    @requires_auth('post:movie')
    def create_movie(jwt):
        data = request.get_json()

        # if requred parameter not exist in the request, abort
        if 'title' not in data and 'release' not in data:
            abort(400)

        # create the movie and insert it
        movie = Movie(title=data['title'], release=data['release'])
        movie.insert()

        return jsonify({'success': True,
                        'movie': movie.format(),
                        'movie_id': movie.id})

    @app.route('/movies/<int:movie_id>', methods=['PATCH'])
    @requires_auth('patch:movie')
    def edit_movie(jwt, movie_id):
        # modify existing movie
        data = request.get_json()

        # retrieve that movie from the database
        movie = Movie.query.get(movie_id)

        # abort if that movie not exist
        if movie is None:
            abort(404)

        # check which attribute to update
        if 'title' in data:
            movie.title = data['title']

        if 'release' in data:
            movie.release = data['release']

        # update it
        movie.update()

        return jsonify({'success': True,
                        'movie': movie.format(),
                        'movie_id': movie_id})

    # ERROR HANDELERS

    @app.errorhandler(AuthError)
    def auth_error(error):
        return (jsonify({'success': False,
                         'error': error.status_code,
                         'message': error.error['description']}),
                error.status_code)

    @app.errorhandler(404)
    def not_found(error):
        return (jsonify({'success': False,
                         'error': 404,
                         'message': 'resource not found'}),
                404)

    @app.errorhandler(400)
    def bad_request(error):
        return (jsonify({'success': False,
                         'error': 400,
                         'message': 'bad request'}),
                400)

    @app.errorhandler(401)
    def unauthorized(error):
        return (jsonify({'success': False,
                         'error': 401,
                         'message': 'unauthorized access'}),
                401)

    return app


APP = create_app()

if __name__ == '__main__':
    APP.run(debug=True)
