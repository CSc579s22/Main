from flask import Flask
from flask import request

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


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
