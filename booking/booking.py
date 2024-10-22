from flask import Flask, render_template, request, jsonify, make_response
import requests
import json
from werkzeug.exceptions import NotFound

app = Flask(__name__)

PORT = 3201
HOST = '0.0.0.0'

SHOWTIME_SERVICE_URL = "http://localhost:3202"

# with open('{}/databases/bookings.json'.format("."), "r") as jsf:
#    bookings = json.load(jsf)["bookings"]

@app.route("/", methods=['GET'])
def home():
   return "<h1 style='color:blue'>Welcome to the Booking service!</h1>"

@app.route("/bookings", methods=['GET'])
def get_bookings():
    bookings = read_bookings()
    return jsonify(bookings), 200

@app.route("/bookings/<string:userid>", methods=['GET'])
def get_booking_for_user(userid):
    bookings = read_bookings()
    for booking in bookings:
        if booking["userid"] == userid:
            return jsonify(booking), 200
    return jsonify({"error": "User ID not found"}), 400

@app.route("/bookings/<string:userid>", methods=['POST'])
def add_booking_for_user(userid):
    bookings = read_bookings()
    req = request.get_json()

    if not req or "date" not in req or "movieid" not in req:
        return jsonify({"error": "Invalid input"}), 400

    movieid = req["movieid"]
    date = req["date"]

    showtime_response = requests.get(f"{SHOWTIME_SERVICE_URL}/showmovies/{date}")
    if showtime_response.status_code != 200:
        return jsonify({"error": "No showtime found for the provided date"}), 404
    
    showtime_data = showtime_response.json()
    if movieid not in showtime_data.get("movies", []):
        return jsonify({"error": "Movie not scheduled for this date"}), 404

    booking = next((b for b in bookings if b["userid"] == userid), None)

    if booking:
        date_item = next((d for d in booking["dates"] if d["date"] == date), None)
        if date_item:
            if movieid in date_item["movies"]:
                return jsonify({"error": "Booking already exists"}), 409

            date_item["movies"].append(movieid)
        else:
            booking["dates"].append({
                "date": date,
                "movies": [movieid]
            })
        write_bookings(bookings)
        return jsonify(booking), 200

    new_booking = {
        "userid": userid,
        "dates": [{
            "date": date,
            "movies": [movieid]
        }]
    }
    bookings.append(new_booking)
    write_bookings(bookings)
    return jsonify(new_booking), 200


def write_bookings(bookings):
    with open('{}/databases/bookings.json'.format("."), 'w') as f:
        json.dump({"bookings": bookings}, f, indent=4)

def read_bookings():
    with open('{}/databases/bookings.json'.format("."), "r") as jsf:
        bookings = json.load(jsf)["bookings"]
    return bookings


if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)
