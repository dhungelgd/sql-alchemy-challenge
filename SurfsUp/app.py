import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from flask import Flask, jsonify


# Database Setup
# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Flask Setup
app = Flask(__name__)

# Flask Routes

@app.route("/")
def homepage():
    """List all the available api routes."""
    return (
        f"List of available Routes for Hawaii Weather Data:<br/><br>"
        f"-- Precipitation: <a href=\"/api/v1.0/precipitation\">/api/v1.0/precipitation<a><br/>"
        f"-- Active Weather Stations: <a href=\"/api/v1.0/stations\">/api/v1.0/stations<a><br/>"
        f"-- Daily Temperature Observations for Station USC00519281 for Last Year: <a href=\"/api/v1.0/tobs\">/api/v1.0/tobs<a><br/>"
        f"-- Min, Average & Max Temperatures for Date Range: /api/v1.0/yyyy-mm-dd/yyyy-mm-dd<a><br>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """ Returns a list of precipitation data for last year"""

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Find the most recent date in the data set.
    most_recent_date = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]

    # Design a query to retrieve the last 12 months of precipitation data and plot the results.
    # Starting from the most recent data point in the database.

    # Calculate the date one year from the last date in data set.
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    ps_query = session.query(measurement.date, measurement.prcp).filter(measurement.date >= last_year).order_by(
        measurement.date)

    # convert the results ti a dictionary
    prcp_dict = {date: prcp for date, prcp in ps_query}

    return jsonify(prcp_dict)


@app.route("/api/v1.0/stations")
def stations():
    """ Returns a list of active stations"""
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # get the list of stations
    station_result = session.query(station.name, station.station).all()
    stations = [{"name": row[0], "station": row[1]} for row in station_result]

    return jsonify(stations)


@app.route("/api/v1.0/tobs")
def tobs():
    """ Returns the temperature observation for most active station"""

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Calculate the date one year from the last date in data set.
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Design a query to find the most active stations (i.e. what stations have the most rows?)
    # List the stations and the counts in descending order.

    active_stations_descending = session.query(measurement.station, func.count(measurement.station)) \
                                .group_by(measurement.station).order_by(func.count(measurement.station).desc()).all()

    most_active_station_id = active_stations_descending[0][0]

    # Using the most active station id
    # Query the last 12 months of temperature observation data for this station and plot the results as a histogram

    temp_data_12_months = session.query(measurement.date, measurement.tobs) \
        .filter(measurement.station == most_active_station_id) \
        .filter(measurement.date >= last_year)\
        .order_by(measurement.date).all()

    # Return a dictionary with the date as key and the daily temperature observation as value
    dates = []
    temp = []

    for date, temperature in temp_data_12_months:
        dates.append(date)
        temp.append(temperature)

    tobs_dict = dict(zip(dates, temp))

    return jsonify(tobs_dict)


@app.route("/api/v1.0/<start>")
def start(start):
    
    """Return a JSON list of the MIN, AVG and MAX temperatures from a given date range."""

    # Create a session from Python to the Database
    session = Session(engine)

    # Query for TMIN, TAVG, and TMAX for the given start date
    lowest_temp = session.query(
        func.min(measurement.tobs).filter(measurement.date >= start)).all()
    highest_temp = session.query(
        func.max(measurement.tobs).filter(measurement.date >= start)).all()
    average_temp = session.query(
        func.avg(measurement.tobs).filter(measurement.date >= start)).all()

    sp_start_data = {'TMIN': lowest_temp, 'TAVG': average_temp, 'TMAX': highest_temp }
    return jsonify(sp_start_data)


@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    """Return a JSON list of the MIN, AVG and MAX temperatures from a given start and end dtae range."""

    # Create a session from Python to the Database
    session = Session(engine)

    # Query for TMIN, TAVG, and TMAX for the given start and end date
    lowest_temp = session.query(
        func.min(measurement.tobs).filter(measurement.date >= start)).filter(measurement.date <= end).all()
    highest_temp = session.query(
        func.max(measurement.tobs).filter(measurement.date >= start)).filter(measurement.date <= end).all()
    average_temp = session.query(
        func.avg(measurement.tobs).filter(measurement.date >= start)).filter(measurement.date <= end).all()

    sp_start_end_data = {'TMIN': lowest_temp, 'TAVG': average_temp, 'TMAX': highest_temp}
    return jsonify(sp_start_end_data)


if __name__ == '__main__':
    app.run(debug=True)

