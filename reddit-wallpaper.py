#!/usr/bin/python

import praw
import requests
from os import path
from subprocess import call

SAVE_LOCATION = path.expanduser('~/.background_image')
SUBREDDIT = 'imaginarylandscapes'
SET_COMMAND = 'feh --bg-fill {}'

def is_image(url):
    r = requests.head(url)
    if(r.headers['content-type']=='image/jpeg'):
        return True
    return False

if __name__=='__main__':
    print SAVE_LOCATION
    r = praw.Reddit(user_agent='reddit-wallpaper')
    subreddit = r.get_subreddit(SUBREDDIT)

    for post in subreddit.get_hot():
        if(is_image(post.url)):
            r = requests.get(post.url)
            with open(SAVE_LOCATION, 'wb') as f:
                for chunk in r.iter_content():
                    f.write(chunk)
            call(SET_COMMAND.format(SAVE_LOCATION), shell=True)
            break
