#!/usr/bin/python

import praw
import requests
import subprocess
import shlex
import time
from os import path

SAVE_LOCATION = path.expanduser('/home/will/.wallpaper')
SUBREDDIT = 'imaginarylandscapes'
SET_COMMAND = 'gsettings set org.gnome.desktop.background picture-uri file://{}'
WINDOW_SESSION_ERROR = 'dconf-WARNING'

def is_image(url):
    r = requests.head(url)
    if(r.headers['content-type']=='image/jpeg'):
        return True
    return False

if __name__=='__main__':
    r = praw.Reddit(user_agent='reddit-wallpaper')
    subreddit = r.get_subreddit(SUBREDDIT)

    for post in subreddit.get_hot():
        if(is_image(post.url)):
            r = requests.get(post.url)
            with open(SAVE_LOCATION, 'wb') as f:
                for chunk in r.iter_content():
                    f.write(chunk)
            run = 1000
            while(run):
                sp = subprocess.Popen(
                        #['ls']
                        shlex.split(SET_COMMAND.format(SAVE_LOCATION)),
                        #shell=True
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                        )
                if not WINDOW_SESSION_ERROR in sp.communicate()[1]:
                    run=False
                else:
                    time.sleep(0.1)
                    run-=1
            break
