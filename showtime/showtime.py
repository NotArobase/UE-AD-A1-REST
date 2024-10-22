from flask import Flask, render_template, request, jsonify, make_response
import json
from werkzeug.exceptions import NotFound

app = Flask(__name__)

PORT = 3202
HOST = '0.0.0.0'

with open('{}/databases/times.json'.format("."), "r") as jsf:
   schedule = json.load(jsf)["schedule"]

@app.route("/", methods=['GET'])
def home():
   return "<h1 style='color:blue'>Welcome to the Showtime service!</h1>"

@app.route("/showtimes", methods=['GET'])
def get_schedule():
    """Return the full JSON schedule"""
    return jsonify({"schedule": schedule}), 200

@app.route("/showmovies/<string:date>", methods=['GET'])
def get_movies_by_date(date):
    """Return movies scheduled for a specific date"""
    # Search for the schedule corresponding to the provided date
    for day_schedule in schedule:
        if day_schedule["date"] == date:
            return jsonify(day_schedule), 200
    
    # If no schedule for the provided date is found
    return make_response(jsonify({"error": "Schedule not found for date: {}".format(date)}), 404)

if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)
