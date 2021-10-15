#
# Python code demonstrating various concurrency and parallelism
# mechanisms in Python.
#
# This code is based on the following InfoWorld article:
#
#   https://www.infoworld.com/article/3632284/python-concurrency-and-parallelism-explained.html
#

import aiohttp
import asyncio
import argparse
import re
import urllib.request as ur


from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool
from timeit import default_timer as timer


URLS = [
    "https://python.org",
    "https://docs.python.org/",
    "https://wikipedia.org",
    "https://imdb.com",
    "https://www.infoworld.com",
    "https://stackoverflow.com",
    "https://code.visualstudio.com",
    "https://www.managersclub.com/",
    "https://apple.com/",
    "https://www.christopherward.com/",
    "https://www.afiniti.com/",
    "https://www.noduswatches.com/",
    "https://www.boldrsupply.co/",
    "https://www.rzewatches.com/",
    "https://usd.farer.com/",
    "https://www.tissotwatches.com/en-en",
    "https://baltic-watches.com/en",
    "https://www.brew-watches.com/",
    "https://www.seikowatches.com/global-en",
    "https://www.midowatches.com/en/",
    "https://www.hanhart.com/en/",
    "https://ravenwatches.com/",
    "https://www.longines.com/",
    "https://lum-tec.com/",
    "https://en.yema.com/",
    "https://www.oris.ch/",
    "https://www.spinnaker-watches.com/",
    "https://danhenrywatches.com/",
]

META_MATCH = re.compile("<meta .*?>")

datas = []


async def get_from_coroutine(session, url):
    async with session.get(url) as r:
        print(f"Fetching data from url {url} ...")
        return await r.text()


def get_from(url):
    connection = ur.urlopen(url)
    data = connection.read()
    datas.append(data)


def get_from_extra(url):
    connection = ur.urlopen(url)
    data = str(connection.read())
    return META_MATCH.findall(data)


def run_task_single_threaded():
    print(f"Fetching data from URLs (single-threaded)")
    for url in URLS:
        # print(f"Processing site: {url}")
        get_from(url)


def run_task_multi_threaded():
    print(f"Fetching data from URLs (multi-threaded)")
    with ThreadPoolExecutor() as ex:
        for url in URLS:
            ex.submit(get_from, url)


async def async_task_launcher():
    print(f"Fetching data from URLs (async/coroutine)")
    async with aiohttp.ClientSession() as session:
        datas = await asyncio.gather(*[get_from_coroutine(session, u) for u in URLS])


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(
        description="Script to experiment with multi-threading and parallelism"
    )

    arg_parser.add_argument(
        "-v",
        "--verbose",
        required=False,
        action="store_true",
        help="display verbose output",
    )

    group = arg_parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-st",
        "--single-threaded",
        action="store_true",
        required=False,
        help="run the tasks using a single-threaded approach",
    )
    group.add_argument(
        "-mt",
        "--multi-threaded",
        action="store_true",
        required=False,
        help="run the tasks using a multi-threaded approach",
    )
    group.add_argument(
        "-as",
        "--async-coroutine",
        action="store_true",
        required=False,
        help="run the tasks using co-routines / async",
    )
    group.add_argument(
        "-mp",
        "--multi-processing",
        action="store_true",
        required=False,
        help="run the tasks using multi-processing",
    )

    args = arg_parser.parse_args()

    if args.single_threaded:
        start = timer()
        run_task_single_threaded()
        end = timer()
        print(f"Single-threaded run: total elapsed time: {end - start}")
        print()
        # print([_[:200] for _ in datas])
        # print()
    elif args.multi_threaded:
        start = timer()
        run_task_multi_threaded()
        end = timer()
        print(f"Multi-threaded run: total elapsed time: {end - start}")
        print()
        # print([_[:200] for _ in datas])
        # print()
    elif args.async_coroutine:
        start = timer()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(async_task_launcher())
        end = timer()
        print(f"Async/Coroutine run: total elapsed time: {end - start}")
        print()
    elif args.multi_processing:
        start = timer()
        with Pool() as p:
            result = p.map(get_from_extra, URLS)
        print(result)
        end = timer()
        print(f"Multi-processing run: total elapsed time: {end - start}")
        print()

    # let's just look at the beginning of each data stream
    # as this could be a lot of data
    # print([_[:200] for _ in datas])
    # print()

    # print(f"Total elapsed time: {end - start}")
