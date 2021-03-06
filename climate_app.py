from dateutil.relativedelta import relativedelta
import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

#import flask
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Base.classes.keys()
Mea=Base.classes.measurement
Sta=Base.classes.station

#create an app
app=Flask(__name__)


#define home route 
@app.route("/")
def home():
    
    print("Server recieved request for Home")
    return (
        f"Honolulu, Hawaii climate results API's!:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>")

session = Session(engine)
rec_date=session.query(Mea.date).order_by(Mea.date.desc()).first()
recent_date=dt.datetime.strptime(rec_date[0],'%Y-%m-%d')
twel_months = recent_date - relativedelta(months=12)
act_stations=session.query(Mea.station, func.count(Mea.date)).group_by(Mea.station).\
order_by(func.count(Mea.station).desc()).all()
station_id=act_stations[0][0]
session.close()

@app.route("/api/v1.0/precipitation")
def precipitation():
    
    session = Session(engine)
    #precipitation query
    dt_prcp=session.query(Mea.date, Mea.prcp).filter(
                        Mea.date>=twel_months).filter(
                        Mea.date.between(
                        twel_months,recent_date)).all()
    
    
    session.close()

# Create a dictionary from the row data and append to a list of all_passengers
    HI_precipitation = []
    for date,prcp in dt_prcp:
        dt_prcp_dict = {}
        dt_prcp_dict["date"]=date
        dt_prcp_dict["prcp"]=prcp
        HI_precipitation.append(dt_prcp_dict)

    return jsonify(HI_precipitation)

@app.route("/api/v1.0/station")
def station():
    session = Session(engine)
    #station query
    only_stations=session.query(Mea.station).group_by(Mea.station).\
    order_by(func.count(Mea.station).desc()).all()
    
    session.close()

    HI_stations = []
    for station in only_stations:
        only_stations_dict = {}
        only_stations_dict["station"]=station
        HI_stations.append(only_stations)

    return jsonify(HI_stations)
    
    
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    #tobs query
    
    last_12= session.query(Mea.date, Mea.tobs).filter(
                        Mea.date >= twel_months).filter(
                        Mea.date <= recent_date).filter(
                        Mea.station == station_id).all()
    
    session.close()

    HI_tobs = []
    for tobs in last_12:
        last_12_dict = {}
        last_12_dict["date"]=tobs
        HI_tobs.append(last_12)

    return jsonify(HI_tobs)
    

@app.route("/api/v1.0/<start_date>")
def start(start_date):
    
    session = Session(engine)
    #start query
    results_start=session.query(func.min(Mea.tobs),func.max(Mea.tobs),func.avg(Mea.tobs)).filter(
        Mea.date>= start_date).all()
    
    session.close()
    # Create a dictionary from the row data and append to a list of start_date_tobs
    tobs_start = []
    for min, avg, max in results_start:
        tobs_start_dict = {}
        tobs_start_dict["min_temp"] = min
        tobs_start_dict["avg_temp"] = avg
        tobs_start_dict["max_temp"] = max
        tobs_start.append(tobs_start_dict)

    return jsonify(tobs_start)


@app.route("/api/v1.0/<start_date>/<end_date>")
def start_end(start_date,end_date):
    
    session = Session(engine)
    #start query
    results_end=session.query(func.min(Mea.tobs),func.max(Mea.tobs),func.avg(Mea.tobs)).filter(
        Mea.date>= start_date).filter(Mea.date<=end_date).all()
    
    session.close()
    # Create a dictionary from the row data and append to a list of start_date_tobs & end_date_tobs
    tobs_start_end = []
    for min, avg, max in results_end:
        tobs_start_end_dict = {}
        tobs_start_end_dict["min_temp"] = min
        tobs_start_end_dict["avg_temp"] = avg
        tobs_start_end_dict["max_temp"] = max
        tobs_start_end.append(tobs_start_end_dict)

    return jsonify(tobs_start_end)


if __name__=="__main__":
    app.run(debug=True)

