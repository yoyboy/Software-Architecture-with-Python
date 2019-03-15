from PIL import Image
import urllib.request
import threading

# root = "/Users/macbook/Documents/GitHub/Software-Architecture-with-Python/myfiles/images/"
root = "./images/"

def thumbnail_image(url, size = (64, 64), format = ".png"):
    im = Image.open(urllib.request.urlopen(url))
    pieces = url.split("/")
    filename = "".join((pieces[-2], "_", pieces[-1].split(".")[0], "_thumb", format))
    im.thumbnail(size, Image.ANTIALIAS)
    im.save(root + filename)
    print("Saved: ", filename)

if __name__ == "__main__":
    img_urls = ['https://dummyimage.com/256x256/000/fff.jpg',
                'https://dummyimage.com/320x240/fff/00.jpg',
                'https://dummyimage.com/640x480/ccc/aaa.jpg',
                'https://dummyimage.com/128x128/ddd/eee.jpg',
                'https://dummyimage.com/720x720/111/222.jpg']
    # img_urls = ['https://dummyimage.com/256x256/000/fff.jpg']

    for url in img_urls:
        # thumbnail_image(url)
        t = threading.Thread(target = thumbnail_image, args = (url, ))
        t.start()