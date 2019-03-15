import threading
import time
import string
import random
import urllib.request
from PIL import Image
from queue import Queue

root = "./images/"

class ThumbnailURL_Generator(threading.Thread):
    def __init__(self, queue, sleep_time = 1):
        self.sleep_time = sleep_time
        self.queue = queue
        self.flag = True
        self._sizes = (240, 320, 360, 480, 600, 720)
        self.url_template = "https://dummyimage.com/%s/%s/%s.jpg"
        threading.Thread.__init__(self, name = "producer")

    def __str__(self):
        return "Producer"

    def get_size(self):
        return "%d x %d" % (random.choice(self._sizes), random.choice(self._sizes))

    def get_color(self):
        return "".join(random.sample(string.hexdigits[:-6], 3))

    def run(self):
        while self.flag:
            url = self.url_template % (self.get_size(), self.get_color(), self.get_color())
            print(self, "Put", url)
            self.queue.put(url)
            time.sleep(self.sleep_time)

    def stop(self):
        self.flag = False

class ThumbnailURL_Consumer(threading.Thread):
    def __init__(self, queue):
        self.queue = queue
        self.flag = True
        threading.Thread.__init__(self, name = "Consumer")

    def __str__(self):
        return "Consumer"

    def thumbnail_image(self, url, size = (64, 64), format = ".png"):
        im = Image.open(urllib.request.urlopen(url))
        filename = url.split("/")[-1].split(".")[0] + "_thumb" + format

        im.thumbnail(size, Image.ANTIALIAS)
        im.save(root + filename)
        print(self, "Saved: ", filename)

    def run(self):
        while self.flag:
            url = self.queue.get()
            print(self, "Got: ", url)
            self.thumbnail_image(url)


    def stop(self):
        self.flag = False

if __name__ == "__main__":
    q = Queue(maxsize = 200)
    producers, consumers = [], []

    for _ in range(2):
        t = ThumbnailURL_Generator(q)
        producers.append(t)
        t.start()

    for _ in range(2):
        t = ThumbnailURL_Consumer(q)
        consumers.append(t)
        t.start()

