import requests
from collections import Counter
import operator

def hound():
    text = requests.get("https://www.gutenberg.org/files/2852/2852-0.txt").text
    c = Counter()
    words = [word.lower().strip() for word in text.split()]
    c.update(words)

    data = sorted(c.items(), key = operator.itemgetter(1), reverse = True)[:10]
    print(data)

if __name__ == "__main__":
    hound()