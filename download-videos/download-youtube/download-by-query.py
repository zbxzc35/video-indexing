import youtube_dl
import socket
import urllib2
import traceback
import urllib
import requests
from lxml import html
import re
import sys

import time
import os
DEST_FOLDER = '/home/ubuntu/panorama/download-periscope/videos'
class MyLogger(object):
    def debug(self, msg):
        print (msg)
        pass


    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')

ydl_opts = {
        'format': 'bestvideo/best',
        'sanitize_filename': True,
        'writeinfojson': True,
        'verbose': True
        #'logger': MyLogger()
        #'progress_hooks': [my_hook],
        }

def replace_extension(filename, ext, expected_real_ext=None):
    name, real_ext = os.path.splitext(filename)
    return '{0}.{1}'.format(
            name if not expected_real_ext or real_ext[1:] == expected_real_ext else filename,
            ext)

def get_metadata(url, filename):

    watch_urls = []
    try:
        html_doc = urllib2.urlopen(url).readlines()

    except urllib2.URLError, e:
        # For Python 2.7
        print 'URLError %r' % e
        return

    except socket.timeout, e:
        # For Python 2.7
        print 'Timeout %r' % e
        return

    with open(filename, 'w') as fh:
        for line in html_doc:
            fh.write(line)



def download_video(urls):
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        for url in urls:
            try:
                #ret, ress = ydl.download([url])
                # !!need to modify youtube-dl source code
                ret, ress = ydl.download([url])
                #print ress[0]['title'], getNewVideoName(ress[0]['title']) 
                prefix = ress[0]['title'] + '-' + ress[0]['id']
                metadata_fname = ress[0]['title'] + '-' + ress[0]['id'] + '.metadata'
                get_metadata(url, metadata_fname)
                new_prefix = getNewVideoName(prefix)
                files = [prefix + '.mp4', prefix  + '.info.json', prefix + '.metadata']
                new_files = [new_prefix + '.mp4', new_prefix  + '.info.json', new_prefix + '.metadata']
                for fid, f in enumerate(files):
                    if os.path.exists(f):
                        os.rename(f, os.path.join(DEST_FOLDER, new_files[fid])) 
            except:
                print 'error:', traceback.format_exc()
                continue

def parse_video_archive(url):
    watch_urls = []
    try:
        html_doc = urllib2.urlopen(url).readlines()

    except urllib2.URLError, e:
        # For Python 2.7
        print 'URLError %r' % e
        return

    except socket.timeout, e:
        # For Python 2.7
        print 'Timeout %r' % e
        return

    urls = []
    for idx, line in enumerate(html_doc):
        line = line.strip()
        if line.find('<span class="label label-danger">Off air!</span>') >= 0:
            # get url
            url_string = html_doc[idx + 3]
            url = url_string[url_string.index('https://'): url_string.index("',")]
            urls += [url]
    return urls

## get new video name without extension
def getNewVideoName(videoname):

    nstr = re.sub(r'[?|$|.|!]',r'', videoname)
    nestr = nestr = re.sub(r'[^a-zA-Z0-9 ]',r'',nstr)
    new_videoname = '_'.join([str(x).lower() for x in nestr.split(' ')]) 

    return new_videoname

def start_download():
    urls = parse_video_archive('http://onperiscope.com/')
    download_video(urls) 

if __name__ == "__main__":

    while True:
        if len(os.listdir(DEST_FOLDER)) >= 1000000 * 3 + 1000:
            break
        start_download()
        time.sleep(2 * 60)
