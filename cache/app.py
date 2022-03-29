from flask import Flask, redirect, request
from time import time
from collections import defaultdict
from fairness import stage1


app = Flask(__name__)
cache_address = "http://10.10.10.8:81"

bitrate_history = defaultdict(lambda: list())
begin_time = {}
total_bw = 1000


# bitrate_list = [89283, 262537, 791182, 2484135, 4219897]
bitrate_map = {
    "360": [89283, 262537],
    "720": [791182],
    "1080": [2484135, 4219897]
}


def get_resolution_by_bitrate(bitrate):
    for resolution in bitrate_map:
        if bitrate in bitrate_map[resolution]:
            return resolution


def calc_fair_bitrate(client, expected_bitrate):
    r_max = []
    res = []
    client_list = []
    expected_resolution = get_resolution_by_bitrate(expected_bitrate)
    for c in bitrate_history.keys():
        client_list.append(c)
        # history for one client
        history = bitrate_history[c]
        # get most recent bitrate
        bitrate = history[-1]["bitrate"]
        resolution = get_resolution_by_bitrate(bitrate)
        res.append(resolution)
        r_max.append(bitrate_map[resolution][-1])
    client_list.append(client)
    res.append(expected_resolution)
    r_max.append(bitrate_map[expected_resolution][-1])
    result = stage1(res, r_max, total_bw)
    print(result)
    return result


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def hello_world(path):
    client = request.remote_addr
    if str.endswith(str(path), ".m4s"):
        requested_bitrate = path.split("/")[2].split("_")[1].split("bps")[0]
        fair_bitrate_list = calc_fair_bitrate(client, requested_bitrate)
        path = path.replace(requested_bitrate, fair_bitrate_list[-1])
        cur_time = time()
        if client not in begin_time.keys():
            begin_time[client] = cur_time
        for i in range(len(bitrate_history.keys())):
            bitrate_history[i].append({"time": cur_time - begin_time[client], "bitrate": fair_bitrate_list[i]})
    url = "{}/{}".format(cache_address, path)
    return redirect(url)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
