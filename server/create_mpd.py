import datetime
import sys
import time
from pathlib import Path

from ffmpeg_streaming import Formats
from ffmpeg_streaming import input

# BigBuckBunny video url
# https://www.youtube.com/watch?v=aqz-KE-bpKQ
# or
# https://s3.us-west-1.wasabisys.com/public-assets/original.mkv

start_time = time.time()


def time_left(time_, total):
    if time_ != 0:
        diff_time = time.time() - start_time
        seconds_left = total * diff_time / time_ - diff_time
        time_left = str(datetime.timedelta(seconds=int(seconds_left))) + ' left'
    else:
        time_left = 'calculating...'

    return time_left


def monitor(ffmpeg, duration, time_, process):
    per = round(time_ / duration * 100)
    sys.stdout.write(
        "\rTranscoding...(%s%%) %s [%s%s]" % (per, time_left(time_, duration), '#' * per, '-' * (100 - per)))
    sys.stdout.flush()


opts = {
    'hide_banner': None,
    'y': None,
    'vsync': 0,
    'hwaccel': 'cuvid',
    'c:v': 'h264_cuvid'
}

video_path = "h264.mp4"
video = input(video_path, pre_opts=opts)
dash = video.dash(Formats.h264('h264_nvenc'))
dash.auto_generate_representations()
Path("result2").mkdir(exist_ok=True)

dash.output('./result2/dash.mpd')
