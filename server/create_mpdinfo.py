#!/usr/bin/env python

from __future__ import division
import mpd_insert

# stars = lambda n: "*" * n
hit_count = {"89283": 0, "262537": 0, "791182": 0, "2484135": 0, "4219897": 0}
mpd_name = "/var/www/html/ftp.itec.aau.at/datasets/DASHDataset2014/BigBuckBunny/2sec/"
for i in range(1, 51):
    f_name = mpd_name + "BigBuckBunny_2s_mod" + str(i) + ".mpd"
    print(f_name)
    mpd_insert.read_mpd(f_name)
