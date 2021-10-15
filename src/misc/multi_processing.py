import urllib.request as ur
from multiprocessing import Pool
import re


urls = [
    "https://python.org",
    "https://docs.python.org",
    "https://wikipedia.org",
    "https://imdb.com",
]

meta_match = re.compile("<meta .*?>")


def get_from(url):
    connection = ur.urlopen(url)
    data = str(connection.read())
    return meta_match.findall(data)


def main():
    with Pool() as p:
        datas = p.map(get_from, urls)
    print(datas)
    print(type(datas))
    # We're not truncating data here,
    # since we're only getting extracts anyway


if __name__ == "__main__":
    main()
