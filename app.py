# Import the dependencies.
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import pandas as pd
import datetime as dt

#################################################
# Database Setup
#################################################


# reflect an existing database into a new model
engine = create_engine("sqlite:///hawaii.sqlite")
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################


@app.route("/")
def welcome():
    return (
        f"Welcome to the Hompage<br/>"
        f"Here are the available routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/yyyy-mm-dd<br/>"
        f"/api/v1.0/yyyy-mm-dd/yyyy-mm-dd")


# ----------------------------------------


@app.route("/api/v1.0/precipitation")
def prec():
    session = Session(engine)
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement.prcp, Measurement.date).filter(
        Measurement.date >= one_year_ago).all()
    session.close()

    variable_one = list(np.ravel(results))

    all_prec = []
    for prec, date in results:
        measurement_dict = {date: prec}

        all_prec.append(measurement_dict)
    return jsonify(all_prec)

# ----------------------------------------


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.station).all()
    stations = list(np.ravel(results))
    return jsonify(stations)


# ----------------------------------------

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    results = session.query(Measurement.station, func.count(Measurement.station)).group_by(
        Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    session.close()
    temp = session.query(func.min(Measurement.tobs), func.max(
        Measurement.tobs)).filter(Measurement.station == "USC00519281").all()
    tobs = list(np.ravel(temp))
    return jsonify(tobs)

# ----------------------------------------


@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def sttenddates(start=None, end=None):
    # start = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    session = Session(engine)

# for loop: if its NOT the end, then run just the start
    if not end:
        results = session.query(func.min(Measurement.tobs), func.avg(
            Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).all()

    #otherwise, if it IS the end, then run the start AND the end
    else:
        results = session.query(func.min(Measurement.tobs), func.avg(
                Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    temps = list(np.ravel(results))

    session.close
    return jsonify(temps=temps)

# ----------------------------------------

if __name__ == '__main__':
    app.run(debug=True)
