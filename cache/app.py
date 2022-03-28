from flask import Flask, redirect, request
from time import time
from collections import defaultdict
from pprint import pprint

app = Flask(__name__)
cache_addr = "http://10.10.10.8:81"

history = defaultdict(lambda: list())
begin_time = {}

bitrate_list = [89283, 262537, 791182, 2484135, 4219897]


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def hello_world(path):
    host = request.remote_addr
    print(host)
    if str.endswith(str(path), ".m4s"):
        bitrate = path.split("/")[2].split("_")[1].split("bps")[0]
        new_bitrate = str(bitrate_list[int(int(host[-1])/2)])
        path = path.replace(bitrate, new_bitrate)
        print("new path: ", path)
        cur_time = time()
        if host not in begin_time.keys():
            begin_time[host] = cur_time
        history[host].append({"time": cur_time - begin_time[host], "bitrate": new_bitrate})
        pprint(history)
    url = "{}/{}".format(cache_addr, path)
    return redirect(url)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
