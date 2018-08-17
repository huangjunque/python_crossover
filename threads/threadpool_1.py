import urllib2
import os
import time
import threadpool

def download_file(url):
    print("begin download {}".format(url))
    urlhandler = urllib2.urlopen(url)
    fname = os.path.basename(url) + ".html"
    with open(fname, "wb") as f:
        while True:
            chunk = urlhandler.read(1024)
            if not chunk:
                break
            f.write(chunk)
urls = ["http://wiki.python.org/moni/WebProgramming",
        "https://www.createspace.com/3611970",
        "http://wiki.python.org/moin/Documention"]
pool_size = 2
pool = threadpool.