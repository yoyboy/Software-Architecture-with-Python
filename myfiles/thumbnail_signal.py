import threading
import time
import string
import random
import urllib.request
from PIL import Image
from queue import Queue
import uuid
import glob

root = "./images/"

class ThumbnailImageSemaSaver:
    def __init__(self, limit = 10):
        self.limit = limit
        self.counter = threading.BoundedSemaphore(value = limit)
        self.count = 0

    def acquire(self):
        return self.counter.acquire(blocking = False)

    def release(self):
        return self.counter.release()

    def thumbnail_image(self, url, size = (64, 64), format = ".png"):
        im = Image.open(urllib.request.urlopen(url))
        pieces = url.split("/")
        filename = "".join((pieces[-2], "_", pieces[-1].split(".")[0], "_thumb", format))
        try:
            im.thumbnail(size, Image.ANTIALIAS)
            im.save(root + filename)
            print("Saved: ", filename)
            self.count += 1
        except Exception as e:
            print("Error saving URL", url, e)
            self.release()

        return True

    def save(self, url):
        if self.acquire():
            self.thumbnail_image(url)
            return True
        else:
            print("Semaphore limit reached, returning False")
            return False

class ThumbnailURL_Consumer(threading.Thread):
    def __init__(self, queue, saver):
        self.queue = queue
        self.saver = saver
        self.flag = True
        self.index = 0
        self._id = uuid.uuid4().hex
        threading.Thread.__init__(self, name = "Consumer-%s" % self._id)

    def __str__(self):
        return "consumer-%s-%s" % (self._id, self.index)

    def run(self):
        while self.flag:
            url = self.queue.get()
            self.index += 1
            print(self, "Got", url)
            if not self.saver.save(url):
                print(self, "Set limit reached, quitting")
                break
    
    def stop(self):
        self.flag = False


class ThumbnailURL_Generator(threading.Thread):
    def __init__(self, queue, sleep_time = 1):
        self.sleep_time = sleep_time
        self.queue = queue
        self.flag = True
        self.index = 0
        self._sizes = (240, 320, 360, 480, 600, 720)
        self.url_template = "https://dummyimage.com/%s/%s/%s.jpg"
        threading.Thread.__init__(self, name = "producer")

    def __str__(self):
        return "Producer-%s" % self.sleep_time

    def get_size(self):
        return "%d x %d" % (random.choice(self._sizes), random.choice(self._sizes))

    def get_color(self):
        return "".join(random.sample(string.hexdigits[:-6], 3))

    def run(self):
        while self.flag:
            url = self.url_template % (self.get_size(), self.get_color(), self.get_color())
            print(self, "Put", url)
            self.index += 1
            self.queue.put(url)
            time.sleep(self.sleep_time)

    def stop(self):
        self.flag = False

if __name__ == "__main__":
    q = Queue(maxsize = 2000)
    index = 0
    saver = ThumbnailImageSemaSaver(limit = 6)

    producers, consumers = [], []
    for _ in range(3):
        if 2 == _:
            t = ThumbnailURL_Generator(q, 10)
        else:
            t = ThumbnailURL_Generator(q)
        producers.append(t)
        t.start()

    for _ in range(5):
        t = ThumbnailURL_Consumer(q, saver)
        consumers.append(t)
        t.start()

    for t in consumers:
        t.join()
        print("Joined", t, flush = True)

    while not q.empty():
        item = q.get()
        index += 1
        print("item: ", item)

    # sumImagePut = sum(x.index for x in producers)
    sumImagePut = 0
    for x in producers:
        print("x.index: ", x, x.index)
        sumImagePut += x.index
    for t in producers:
        t.stop()
        print("Stoped", t, flush = True)
    
    print("sumImagePut: ", sumImagePut, index)

    print("Total number of PNG images", len(glob.glob(root + "*.png")))