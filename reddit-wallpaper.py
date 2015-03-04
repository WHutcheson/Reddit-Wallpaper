#!/usr/bin/python

import praw
import requests
import subprocess
import shlex
import time
import argparse
from os import path

parser = argparse.ArgumentParser(description='Updates wallpaper from reddit sub.')
parser.add_argument('--subreddit', '-s', nargs='?',
        default='imaginarylandscapes',
        help='name of subreddit')
parser.add_argument('--command', '-c', nargs='?',
        default='gsettings set org.gnome.desktop.background picture-uri file://{}',
        help='command to set wallpaper.  Add {} for file location')

args = parser.parse_args()

SAVE_LOCATION = path.expanduser('~/.wallpaper')
SUBREDDIT = args.subreddit
SET_COMMAND = args.command

def is_image(url):
    r = requests.head(url)
    if(r.headers['content-type']=='image/jpeg'):
        return True
    return False

if __name__=='__main__':
    r = praw.Reddit(user_agent='reddit-wallpaper')
    subreddit = r.get_subreddit(SUBREDDIT)

    try:
        for post in subreddit.get_hot():
            if(is_image(post.url)):
                r = requests.get(post.url)
                with open(SAVE_LOCATION, 'wb') as f:
                    for chunk in r.iter_content():
                        f.write(chunk)
                sp = subprocess.Popen(
                    shlex.split(SET_COMMAND.format(SAVE_LOCATION)),
                    )
                break;
    except requests.exceptions.HTTPError:
        print 'Error: Unknown subreddit {}'.format(SUBREDDIT)
        exit()
