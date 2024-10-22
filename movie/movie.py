from flask import Flask, render_template, request, jsonify, make_response
import json

app = Flask(__name__)

PORT = 3200
HOST = '0.0.0.0'


# root message
@app.route("/", methods=['GET'])
def home():
    return make_response("<h1 style='color:blue'>Welcome to the Movie service!</h1>",200)

@app.route("/json", methods=['GET'])
def get_json():
    movies = read_movies()
    res = make_response(jsonify(movies), 200)
    return res

@app.route("/movies/<movieid>", methods=['GET'])
def get_movie_byid(movieid):
    movies = read_movies()
    for movie in movies:
        if str(movie["id"]) == str(movieid):
            res = make_response(jsonify(movie),200)
            return res
    return make_response(jsonify({"error":"Movie ID not found"}),400)

@app.route("/moviesbytitle", methods=['GET'])
def get_movie_bytitle():
    movies = read_movies()
    # Check if the title parameter is provided in the query string
    title = request.args.get('title')

    if not title:
        return make_response(jsonify({"error": "Missing 'title' parameter"}), 400)

    # Search for the movie by title in the movies list
    for movie in movies:
        if movie["title"].lower() == title.lower():  # Case-insensitive comparison
            return make_response(jsonify(movie), 200)

    # If the movie is not found, return an error
    return make_response(jsonify({"error": "Movie title not found"}), 404)

@app.route("/movies/<movieid>", methods=['POST'])
def add_movie(movieid):
    movies = read_movies()
    req = request.get_json()

    for movie in movies:
        if str(movie["id"]) == str(movieid):
            return make_response(jsonify({"error":"movie ID already exists"}),409)

    movies.append(req)
    write_movies(movies)
    res = make_response(jsonify({"message":"movie added"}),200)
    return res

@app.route("/movies/<movieid>/<rate>", methods=['PUT'])
def update_movie_rating(movieid, rate):
    movies = read_movies()
    for movie in movies:
        if str(movie["id"]) == str(movieid):
            movie["rating"] = rate
            res = make_response(jsonify(movie),200)
            return res

    res = make_response(jsonify({"error":"movie ID not found"}),201)
    return res

@app.route("/movies/<movieid>", methods=['DELETE'])
def del_movie(movieid):
    movies = read_movies()
    for movie in movies:
        if str(movie["id"]) == str(movieid):
            movies.remove(movie)
            write_movies(movies)
            return make_response(jsonify(movie),200)
    res = make_response(jsonify({"error":"movie ID not found"}),400)
    return res


def write_movies(movies):
    with open('{}/databases/movies.json'.format("."), 'w') as f:
        json.dump({"movies": movies}, f, indent=4)

def read_movies():
    with open('{}/databases/movies.json'.format("."), "r") as jsf:
        movies = json.load(jsf)["movies"]
    return movies

if __name__ == "__main__":
    print(f"Server running on port {PORT}")
    app.run(host=HOST, port=PORT)
