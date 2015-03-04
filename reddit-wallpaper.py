#!/usr/bin/python

import praw
import requests
import subprocess
import shlex
import argparse
import platform
from os import path
from PIL import Image

WALLPAPER_LOCATION = path.expanduser('~/.wallpaper')
PREVIOUS_URL_LOCATION = path.abspath('/tmp/reddit-wallpaper-url')

COMMANDS = {'Linux': 
                    'gsettings set org.gnome.desktop.background picture-uri file://{}',
            'Darwin':
                    """/usr/bin/osascript<<END
                    tell application "Finder"
                    set desktop picture to POSIX file "{}"
                    end tell
                    END"""
            }

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

def check_image_dimentions(f, ratio):
    im = Image.open(f)
    r1 = float(ratio[0])/float(ratio[1])
    r2 = float(im.size[0])/float(im.size[1])
    return 0.90 <= r1/r2 <= 1.10

def load_previous_urls():
    try:
        with open(PREVIOUS_URL_LOCATION, 'r') as f:
            x = [x for x in f.read().split('\n')][:-1]
        return x
    except IOError:
        return []

def save_urls(urls):
    with open(PREVIOUS_URL_LOCATION, 'w') as f:
        for url in checked:
            f.write(url + '\n')

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Updates wallpaper from reddit sub.')
    parser.add_argument('--subreddit', '-s', nargs='?',
        default='imaginarylandscapes',
        help='Name of subreddit')
    parser.add_argument('--command', '-c', nargs='?',
        default='',
        help='Command to set wallpaper.  Add {} for file location')
    parser.add_argument('--ratio', '-r', nargs='?',
            default='16:9',
        help='Aspect ratio for images.')

    args = parser.parse_args()
    ratio = [int(x) for x in args.ratio.split(':')]

    print 'Starting reddit-wallpaper'
    print 'Subreddit: {}'.format(args.subreddit)
    r = praw.Reddit(user_agent='reddit-wallpaper')
    subreddit = r.get_subreddit(args.subreddit)

    previous = load_previous_urls()
    checked = []

    if args.command:
        command = args.command
    else:
        if not COMMANDS.has_key(platform.system()):
            print "Unknown command to change wallpaper"
            exit()
        command = COMMANDS[platform.system()]

    try:
        for post in subreddit.get_hot():
            if(is_image(post.url)):
                checked.append(post.url)
                if(previous and post.url==previous[-1]):
                    print "Image not changed"
                    save_urls(checked)
                    break
                if(post.url in previous):
                    print "Skipping image: {}".format(post.url)
                    continue
                print "Downloading: {}".format(post.url)
                r = requests.get(post.url)
                with open(WALLPAPER_LOCATION, 'wrb') as f:
                    for chunk in r.iter_content():
                        f.write(chunk)
                if(not check_image_dimentions(WALLPAPER_LOCATION, ratio)):
                    print "Image aspect wrong"
                    continue;
                sp = subprocess.Popen(
                    shlex.split(command.format(WALLPAPER_LOCATION)),
                    )
                print "Background successfully set"
                save_urls(checked)
                print "URL file written to {}".format(PREVIOUS_URL_LOCATION)
                break;
    except requests.exceptions.HTTPError:
        print 'Error: Unknown subreddit {}'.format(args.subreddit)
        exit()
    except praw.errors.RedirectException:
        print 'Error: Unknown subreddit {}'.format(args.subreddit)
        exit()
