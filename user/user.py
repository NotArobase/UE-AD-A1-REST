from flask import Flask, request, jsonify, make_response
import requests
import json

app = Flask(__name__)

BOOKING_SERVICE_URL = "http://localhost:3201"
MOVIE_SERVICE_URL = "http://localhost:3200"

PORT = 3203
HOST = '0.0.0.0'

with open('{}/databases/users.json'.format("."), "r") as jsf:
    users = json.load(jsf)["users"]

@app.route("/", methods=['GET'])
def home():
    return "<h1 style='color:blue'>Welcome to the User service!</h1>"

@app.route("/users", methods=['GET'])
def get_all_users():
    return jsonify(users), 200

@app.route("/users/<string:userid>/bookings", methods=['GET'])
def get_user_bookings(userid):
    user = next((u for u in users if u['id'] == userid), None)
    if not user:
        return make_response(jsonify({"error": "User ID not found"}), 404)

    booking_url = f"{BOOKING_SERVICE_URL}/bookings/{userid}"

    booking_response = requests.get(booking_url)

    if booking_response.status_code != 200:
        return make_response(jsonify({"error": "No bookings found"}), 404)

    return jsonify(booking_response.json()), 200

@app.route("/users/<string:userid>/bookings/<string:date>", methods=['GET'])
def get_user_bookings_by_date(userid,date):
    user = next((u for u in users if u['id'] == userid), None)
    if not user:
        return make_response(jsonify({"error": "User ID not found"}), 404)

    booking_url = f"{BOOKING_SERVICE_URL}/bookings/{userid}"

    booking_response = requests.get(booking_url)

    if booking_response.status_code != 200:
        return make_response(jsonify({"error": "No bookings found for this date"}), 404)

    response = booking_response.json()

    for date_item in response["dates"]:
        if date_item["date"] == date:
            return jsonify({"userid": userid, "date": date_item["date"], "movies": date_item["movies"]}), 200
    return jsonify({"error": "No bookings found for the specified date"}), 404

@app.route("/users/<string:userid>/movies", methods=['GET'])
def get_user_movies(userid):
    user = next((u for u in users if u['id'] == userid), None)
    if not user:
        return make_response(jsonify({"error": "User ID not found"}), 404)

    booking_url = f"{BOOKING_SERVICE_URL}/bookings/{userid}"
    booking_response = requests.get(booking_url)

    if booking_response.status_code != 200:
        return make_response(jsonify({"error": "No bookings found"}), 404)

    bookings = booking_response.json()

    movie_ids = []
    for booking in bookings.get('dates', []):
        movie_ids.extend(booking.get('movies', []))

    movies_details = []
    for movieid in movie_ids:
        movie_response = requests.get(f"{MOVIE_SERVICE_URL}/movies/{movieid}")
        if movie_response.status_code == 200:
            movies_details.append(movie_response.json())

    if not movies_details:
        return make_response(jsonify({"error": "No movies found for the user's bookings"}), 404)

    return jsonify(movies_details), 200


@app.route("/users/<string:userid>/bookings", methods=['POST'])
def add_user_booking(userid):
    req_data = request.get_json()

    if not req_data or "date" not in req_data or "movieid" not in req_data:
        return make_response(jsonify({"error": "Invalid input"}), 400)

    movieid = req_data["movieid"]
    date = req_data["date"]

    payload = {
        "movieid": movieid,
        "date": date
    }

    booking_url = f"{BOOKING_SERVICE_URL}/bookings/{userid}"
    booking_response = requests.post(booking_url, json=payload)

    if booking_response.status_code == 200:
        return jsonify(booking_response.json()), 200
    elif booking_response.status_code == 404:
        return make_response(jsonify({"error": "Movie or showtime not found"}), 404)
    elif booking_response.status_code == 409:
        return make_response(jsonify({"error": "Booking already exists"}), 409)
    else:
        return make_response(jsonify({"error": "An error occurred while processing the booking"}), 500)
    

@app.route("/users/<string:userid>/bookingsbytitle", methods=['POST'])
def add_user_booking_by_title(userid):
    req_data = request.get_json()

    if not req_data or "date" not in req_data or "title" not in req_data:
        return make_response(jsonify({"error": "Invalid input"}), 400)

    title = req_data["title"]
    date = req_data["date"]

    movie_url = f"{MOVIE_SERVICE_URL}/moviesbytitle"
    movie_response = requests.get(movie_url, params={'title': title})

    if movie_response.status_code == 404:
        return make_response(jsonify({"error": "Movie not found"}), 404)
    movieid = movie_response.json().get('id')
    payload = {
        "movieid": movieid,
        "date": date
    }

    booking_url = f"{BOOKING_SERVICE_URL}/bookings/{userid}"
    booking_response = requests.post(booking_url, json=payload)

    if booking_response.status_code == 200:
        return jsonify(booking_response.json()), 200
    elif booking_response.status_code == 404:
        return make_response(jsonify({"error": "Movie or showtime not found"}), 404)
    elif booking_response.status_code == 409:
        return make_response(jsonify({"error": "Booking already exists"}), 409)
    else:
        return make_response(jsonify({"error": "An error occurred while processing the booking"}), 500)
    

@app.route("/users/movies/<string:movieid>", methods=['GET'])
def get_movie_by_id(movieid):
    movie_url = f"{MOVIE_SERVICE_URL}/movies/{movieid}"
    movie_response = requests.get(movie_url)

    if movie_response.status_code == 200:
        return jsonify(movie_response.json()), 200
    elif movie_response.status_code == 400:
        return make_response(jsonify({"error": "Movie ID not found"}), 400)
    else:
        return make_response(jsonify({"error": "An error occurred while retrieving the movie"}), 500)

@app.route("/users/moviesbytitle", methods=['GET'])
def get_movie_by_title():
    if request.args and 'title' in request.args:
        title = request.args['title']
        movie_url = f"{MOVIE_SERVICE_URL}/moviesbytitle"
        movie_response = requests.get(movie_url, params={'title': title})

        if movie_response.status_code == 200:
            return jsonify(movie_response.json()), 200
        elif movie_response.status_code == 400:
            return make_response(jsonify({"error": "Movie title not found"}), 400)
        else:
            return make_response(jsonify({"error": "An error occurred while retrieving the movie"}), 500)
    return make_response(jsonify({"error": "Invalid input"}), 400)

@app.route("/users/movies/<string:movieid>", methods=['POST'])
def add_movie(movieid):
    req_data = request.get_json()

    if not req_data or "title" not in req_data or "rating" not in req_data:
        return make_response(jsonify({"error": "Invalid input"}), 400)

    movie_url = f"{MOVIE_SERVICE_URL}/movies/{movieid}"
    movie_response = requests.post(movie_url, json=req_data)

    if movie_response.status_code == 200:
        return jsonify(movie_response.json()), 200
    elif movie_response.status_code == 409:
        return make_response(jsonify({"error": "Movie ID already exists"}), 409)
    else:
        return make_response(jsonify({"error": "An error occurred while adding the movie"}), 500)

@app.route("/users/movies/<string:movieid>/rate/<string:rate>", methods=['PUT'])
def update_movie_rating(movieid, rate):
    movie_url = f"{MOVIE_SERVICE_URL}/movies/{movieid}/{rate}"
    movie_response = requests.put(movie_url)

    if movie_response.status_code == 200:
        return jsonify(movie_response.json()), 200
    elif movie_response.status_code == 201:
        return make_response(jsonify({"error": "Movie ID not found"}), 201)
    else:
        return make_response(jsonify({"error": "An error occurred while updating the rating"}), 500)

@app.route("/users/movies/<string:movieid>", methods=['DELETE'])
def delete_movie(movieid):
    movie_url = f"{MOVIE_SERVICE_URL}/movies/{movieid}"
    movie_response = requests.delete(movie_url)

    if movie_response.status_code == 200:
        return jsonify(movie_response.json()), 200
    elif movie_response.status_code == 400:
        return make_response(jsonify({"error": "Movie ID not found"}), 400)
    else:
        return make_response(jsonify({"error": "An error occurred while deleting the movie"}), 500)



if __name__ == "__main__":
    print(f"Server running on port {PORT}")
    app.run(host=HOST, port=PORT)
