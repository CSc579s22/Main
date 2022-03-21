from datetime import datetime, timedelta

import pmdarima as pm
import pymongo
import numpy as np
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure


class ARIMA:
    def __init__(self, *args, **kwargs):
        try:
            self.client = MongoClient(kwargs["MongoURL"])
            self.db = self.client.opencdn
            self.table_port_monitor = self.db.portmonitor
            self.table_server_bandwidth = self.db.server_bandwidth
            print("Connected to MongoDB")
        except ConnectionFailure as e:
            print("MongoDB connection failed: %s" % e)
            exit(1)

    def predict(self, dpid, portno):
        arima_in = []
        for res in self.table_port_monitor.find({"dpid": dpid, "portno": portno}). \
                sort([("_id", pymongo.DESCENDING)]).limit(10):
            # print("res: ", res)x
            arima_in.append(res["RXbandwidth"])

        arima_in.reverse()
        if len(arima_in) == 0:
            return 0.0
        if len(arima_in) < 10 or np.var(arima_in) == 0:
            return np.average(arima_in)

        model = pm.auto_arima(pm.c(arima_in))

        # make your forecasts
        result = model.predict(5)
        sum_arima = 0.0
        for v in result:
            sum_arima += v
        avg_arima = sum_arima / len(result)
        if avg_arima < 0:
            avg_arima = 0
        return avg_arima

    def predict_avg(self, dpid, portno):
        arima_in = []
        for res in self.table_port_monitor.find({"dpid": dpid, "portno": portno,
                                                 "date": {"$gte": datetime.utcnow() - timedelta(seconds=10)}}). \
                sort([("_id", pymongo.DESCENDING)]):
            arima_in.append(res["RXbandwidth"])
        if len(arima_in) == 0:
            return 0.0
        avg_arima = sum(arima_in) / len(arima_in)
        if avg_arima < 0:
            avg_arima = 0
        return avg_arima


if __name__ == "__main__":
    arima = ARIMA(MongoURL="127.0.0.1")
    dpid = "0000aae305428d4a"
    portno = 20
    print(arima.predict(dpid, portno))
