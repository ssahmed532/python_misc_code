#
# Python code demonstrating various concurrency and parallelism
# mechanisms in Python.
#
# This code is based on the following InfoWorld article:
#
#   https://www.infoworld.com/article/3632284/python-concurrency-and-parallelism-explained.html
#

from typing import final
import aiohttp
import asyncio
import argparse
import re
import urllib.request as ur

import hash_utils


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
    "https://halioswatches.com/",
    "https://www.hamiltonwatch.com/",
    "https://www.rado.com/",
    "https://www.fossil.com/en-us/",
]

META_MATCH = re.compile("<meta .*?>")

datas = []

final_results = {}

args = None


async def get_from_coroutine(session, url):
    async with session.get(url) as r:
        print(f"Fetching data from url {url} ...")
        return await r.text()


def get_data_from_url(url):
    """Get data from the specified Web URL. This function is meant to
       simulate an IO and CPU intensive workload.

    Args:
        url (str): a URL to a website
    """

    connection = ur.urlopen(url)

    data = str(connection.read())

    matches = META_MATCH.findall(data)
    if matches:
        data = data + str(matches)

    hash_value0 = hash_utils.calc_str_hash_SHA224(data)
    hash_value1 = hash_utils.calc_str_hash_SHA256(data + hash_value0)
    hash_value2 = hash_utils.calc_str_hash_SHA384(data + hash_value1 + hash_value0)
    hash_value3 = hash_utils.calc_str_hash_SHA512(
        data + hash_value2 + hash_value1 + hash_value0
    )
    hash_value4 = hash_utils.calc_str_hash_Blake2b(
        data + hash_value3 + hash_value2 + hash_value1 + hash_value0
    )
    hash_value5 = hash_utils.calc_str_hash_SHA3_512(
        data + hash_value4 + hash_value3 + hash_value2 + hash_value1 + hash_value0
    )

    final_results[url] = hash_value5


def get_from_extra(url):
    connection = ur.urlopen(url)
    data = str(connection.read())
    return META_MATCH.findall(data)


def run_task_single_threaded():
    for url in URLS:
        get_data_from_url(url)


def run_task_multi_threaded():
    with ThreadPoolExecutor() as ex:
        for url in URLS:
            ex.submit(get_data_from_url, url)


async def async_task_launcher():
    print(f"Fetching data from URLs (async/coroutine)")
    async with aiohttp.ClientSession() as session:
        datas = await asyncio.gather(*[get_from_coroutine(session, u) for u in URLS])


def print_final_results() -> None:
    for key in final_results.keys():
        print(f"{key} -->> {final_results[key]}")

    print()


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
        print(f"Running tasks (single-threaded)")

        start = timer()
        run_task_single_threaded()
        end = timer()

        if args.verbose:
            print_final_results()

        print(f"Single-threaded run: total elapsed time: {end - start}")
        print()
    elif args.multi_threaded:
        print(f"Running tasks (multi-threaded)")

        start = timer()
        run_task_multi_threaded()
        end = timer()

        if args.verbose:
            print_final_results()

        print(f"Multi-threaded run: total elapsed time: {end - start}")
        print()
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
