# Import the dependencies.
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
#Measurement = Base.classes.hawaii_measurements  
#Station = Base.classes.hawaii_stations

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
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Calculate the date 12 months ago from the most recent date
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    twelve_months_ago = pd.to_datetime(most_recent_date) - pd.DateOffset(months=12)
    
    # Query precipitation data for the last 12 months
    results = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= twelve_months_ago.strftime('%Y-%m-%d')).all()
    #results = session.query(Measurement.date, Measurement.prcp).\
     #           filter(Measurement.date >= twelve_months_ago).all()
    
    # Convert results into a dictionary with date as key and precipitation as value
    precipitation_data = {date: prcp for date, prcp in results}
    
    return jsonify(precipitation_data)

@app.route("/api/v1.0/stations")
def stations():
    # Query all stations from the dataset
    stations = session.query(Station.station).distinct().all()
    
    # Extract station names from the query results
    station_list = [station[0] for station in stations]
    
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    # Find the most active station
    most_active_station = session.query(Measurement.station, func.count(Measurement.id)).\
                            group_by(Measurement.station).\
                            order_by(func.count(Measurement.id).desc()).first()[0]
    
    # Calculate the date 12 months ago from the most recent date
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    twelve_months_ago = pd.to_datetime(most_recent_date) - pd.DateOffset(months=12)
    
    # Query temperature observations for the last 12 months for the most active station
    results = session.query(Measurement.date, Measurement.tobs).\
                filter(Measurement.station == most_active_station).\
                filter(Measurement.date >= twelve_months_ago).all()
    
    # Convert results into a list of dictionaries
    temperature_data = [{"date": date, "tobs": tobs} for date, tobs in results]
    
    return jsonify(temperature_data)

@app.route("/api/v1.0/<start>")
def temperature_start(start):
    # Query minimum, average, and maximum temperatures from the start date to the latest date
    temperatures = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                    filter(Measurement.date >= start).all()
    
    # Extract results
    tmin, tavg, tmax = temperatures[0]
    
    # Create a dictionary to hold the temperature data
    temperature_data = {
        "TMIN": tmin,
        "TAVG": tavg,
        "TMAX": tmax
    }
    
    return jsonify(temperature_data)

@app.route("/api/v1.0/<start>/<end>")
def temperature_start_end(start, end):
    # Query minimum, average, and maximum temperatures from the start date to the end date
    temperatures = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                    filter(Measurement.date >= start).\
                    filter(Measurement.date <= end).all()
    
    # Extract results
    tmin, tavg, tmax = temperatures[0]
    
    # Create a dictionary to hold the temperature data
    temperature_data = {
        "TMIN": tmin,
        "TAVG": tavg,
        "TMAX": tmax
    }
    
    return jsonify(temperature_data)

if __name__ == '__main__':
    app.run(debug=True)