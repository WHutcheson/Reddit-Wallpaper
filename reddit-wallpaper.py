#!/usr/bin/python

import praw
import requests
import subprocess
import shlex
import argparse
from os import path

WALLPAPER_LOCATION = path.expanduser('~/.wallpaper')
PREVIOUS_URL_LOCATION = path.abspath('/tmp/reddit-wallpaper-url')

def is_image(url):
    r = requests.head(url)
    if(r.headers['content-type']=='image/jpeg'):
        return True
    return False

def equals_previous(url):
    try:
        with open(PREVIOUS_URL_LOCATION) as f:
            previous_url = f.read()
            return url==previous_url
    except IOError:
        print "No previous url file"
        return False


if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Updates wallpaper from reddit sub.')
    parser.add_argument('--subreddit', '-s', nargs='?',
        default='imaginarylandscapes',
        help='name of subreddit')
    parser.add_argument('--command', '-c', nargs='?',
        default='gsettings set org.gnome.desktop.background picture-uri file://{}',
        help='command to set wallpaper.  Add {} for file location')

    args = parser.parse_args()

    print 'Starting reddit-wallpaper'
    print 'Subreddit: {}'.format(args.subreddit)
    r = praw.Reddit(user_agent='reddit-wallpaper')
    subreddit = r.get_subreddit(args.subreddit)

    try:
        for post in subreddit.get_hot():
            if(is_image(post.url)):
                if(equals_previous(post.url)):
                    print "Image not changed"
                    break;
                print "Found image at: {}".format(post.url)
                r = requests.get(post.url)
                with open(WALLPAPER_LOCATION, 'wb') as f:
                    for chunk in r.iter_content():
                        f.write(chunk)
                sp = subprocess.Popen(
                    shlex.split(args.command.format(WALLPAPER_LOCATION)),
                    )
                print "Background successfully set"
                with open(PREVIOUS_URL_LOCATION, 'w') as f:
                    f.write(post.url)
                print "URL file written to {}".format(PREVIOUS_URL_LOCATION)
                break;
    except requests.exceptions.HTTPError:
        print 'Error: Unknown subreddit {}'.format(args.subreddit)
        exit()
