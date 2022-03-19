from bson import json_util
from flask import Flask
from flask import request
from flask_pymongo import PyMongo
from config import MongoURI

app = Flask(__name__)
app.config["MONGO_URI"] = "{}/opencdn".format(MongoURI)
mongo = PyMongo(app)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/dpid/<dpid>/port/<int:portno>")
def get_port(dpid, portno):
    port = mongo.db.portinfo.find({"dpid": dpid, "portno": portno}).limit(1)
    return json_util.dumps(port[0])


@app.route("/mpd/<name>")
def get_mpd(name):
    return "mpd: " + name


@app.route("/nearest_cache")
def get_nearest_cache_server():
    ip = request.args.get('ip')
    # TODO: verify ip
    return "nearest cache server for: " + ip


if __name__ == "__main__":
    app.run()
