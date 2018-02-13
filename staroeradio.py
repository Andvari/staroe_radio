# -*- coding: utf-8 -*-
from urllib.request import urlopen, Request
from urllib.error import URLError
import requests

import os
import re
import time

error_string = "A PHP Error was encountered"

PATH = "/home/nemo/hdd2Tb/SR"

d = ['А','Б','В','Г','Д','Е','Ж','З','И','К','Л','М','Н','О','П','Р','С','Т','У','Ф','Х','Ц','Ч','Ш','Щ','Э','Ю','Я','0-9']


def unwrap(s, tag):
    open_tag = "<" + tag + ">"
    close_tag = "</" + tag + ">"
    return s[s.find(open_tag)+len(open_tag): s.find(close_tag)]


def wrap(s, tag):
    open_tag = "<" + tag + ">"
    close_tag = "</" + tag + ">"
    return open_tag + s + close_tag


def get_folder(n):
    p = int(n)
    if p < 10000:
        return '0'
    if p < 20000:
        return '10000'
    if p < 30000:
        return '20000'
    if p < 40000:
        return '30000'
    if p < 50000:
        return '40000'
    if p < 60000:
        return '50000'
    if p < 70000:
        return '60000'
    if p < 80000:
        return '70000'
    if p < 90000:
        return '80000'


def scanner():

    for let in d:
        print(let)
        file = open(PATH + "/" + let + ".txt", "w")
        let = str(let.encode('utf-8'))[2: -1].replace('\\x', '%').upper()
        page = urlopen('http://staroeradio.ru/collection/' + let).read().decode('utf-8')
        l = page[page.find("mp3list grid_9") + 18: page.find("grid_9 footer")-19]

        tracks = re.compile("<a href=\"(.*?)</a>").findall(l)
        for track in tracks:
            track_id = track[track.find("/audio")+7: track.find("\"")]

            if track.find("reportage.su") != -1:
                host = "reportage.su"
                url = "http://server.audiopedia.su:8888/get_mp3_project_1.php?site=reportage&id="
                answer = requests.head(url + track_id)
            elif track.find("svidetel.su") != -1:
                host = "svidetel.su"
                url = "http://server.audiopedia.su:8888/get_mp3_project_1.php?site=svidetel&id="
                answer = requests.head(url + track_id)
            elif track.find("theatrologia.su") != -1:
                host = "theatrologia.su"
                url = "http://server.audiopedia.su:8888/get_mp3_project_1.php?site=svidetel&id="
                answer = requests.head(url + track_id)
            elif track.find("lektorium.su") != -1:
                host = "lektorium.su"
                url = "http://server.audiopedia.su:8888/get_mp3_project_1.php?site=lektorium&id="
                answer = requests.head(url + track_id)
            else:
                host = "staroeradio.ru"
                url32 = "http://server.audiopedia.su:8888/get_mp3_32.php?id="
                url128 = "http://server.audiopedia.su:8888/get_mp3_128.php?id="
                try:
                    answer = requests.head(url128+track_id)
                except URLError:
                    answer = requests.head(url32+track_id)
                    print("url error: ", url128)

            if len(answer.headers['Content-Length']) == 0:
                origin_length = '0'
            else:
                origin_length = answer.headers['Content-Length']

            title = track[track.find("mp3name")+9:]
            title = title[: title.find("<")]
            record = wrap(track_id, 'id') + wrap(host, 'host') + wrap(origin_length, 'length') + wrap(title, 'title')
            print(record)
            file.write(record + "\n")

# http://server.audiopedia.su:8888/get_mp3_32.php?id=
# http://server.audiopedia.su:8888/get_mp3_project_1.php?site=theatrologia&id=
# http://server.audiopedia.su:8888/get_mp3_project_1.php?site=reportage&id=
# http://server.audiopedia.su:8888/get_mp3_project_1.php?site=svidetel&id=
# http://server.audiopedia.su:8888/get_mp3_project_1.php?site=lektorium&id=


def verifier():

    to_load   = open(PATH + "/need_to_load.txt", "w")
    to_reload = open(PATH + "/need_to_reload.txt", "w")

    counter = 10
    for let in d:
        print(let)
        file = open(PATH + "/" + let + ".txt", "r")
        for track in file:
            track_id = unwrap(track, "id")
            track_host = unwrap(track, "host")
            track_title = unwrap(track, "title")
            track_length = unwrap(track, "length")

            folder = get_folder(track_id)
            path = (PATH + "/" + folder + "/" + track_id + ".mp3")
            try:
                length = os.path.getsize(path)
                if track_host == 'staroeradio.ru':
                    if int(length) != int(track_length):
                        to_reload.write(wrap(track_id, 'id') + wrap(track_host, "host") + wrap(track_title, 'title') + "\n")
            except FileNotFoundError:
                to_load.write(wrap(track_id, 'id') + wrap(track_host, "host") + wrap(track_title, 'title') + "\n")

    to_reload.close()
    to_load.close()

def redownloader():
    url32 = "http://server.audiopedia.su:8888/get_mp3_32.php?id="
    url128 = "http://server.audiopedia.su:8888/get_mp3_128.php?id="

    for d in range(0, 2):
        for filenum in range(d*10000, d*10000+10000):

            path = (PATH + "/" + str(d * 10000) + "/" + str(filenum) + ".mp3")
            #print(path, end = "..")
            try:
                size = os.path.getsize(path)
            except FileNotFoundError:
                #print("Not Found")
                continue

            if size:
                #print("OK")
                continue

            try:
                req = urlopen(url128 + str(filenum))
                print(url128 + str(filenum))
            except URLError:
                req = urlopen(url32 + str(filenum))
                print(url32 + str(filenum))

            page = req.read()
            track = open(path, "wb")
            track.write(page)
            track.close()


    print("OK")


if __name__ == '__main__':
    verifier()
    #scanner()
    # parser()
    #redownloader()
