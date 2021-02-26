import os
import sys
import timeit

import hashutils


NDIGITS_ROUNDING = 4


def calculate_hashes_sha1(dir_path):
    for filename in os.listdir(dir_path):
        f = os.path.join(dir_path, filename)
        if os.path.isfile(f):
            hashutils.computeFileHashSHA1(f)


def calculate_hashes_sha256(dir_path):
    for filename in os.listdir(dir_path):
        f = os.path.join(dir_path, filename)
        if os.path.isfile(f):
            hashutils.computeFileHashSHA256(f)


def calculate_hashes_sha512(dir_path):
    for filename in os.listdir(dir_path):
        f = os.path.join(dir_path, filename)
        if os.path.isfile(f):
            hashutils.computeFileHashSHA512(f)


def calculate_hashes_blake2b(dir_path):
    for filename in os.listdir(dir_path):
        f = os.path.join(dir_path, filename)
        if os.path.isfile(f):
            hashutils.computeFileHashBlake2b(f)



if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('Usage: python benchmark_hash_functions.py <dirPath containing lots of files>', file=sys.stderr)
        sys.exit(1)

    dir_path = os.path.abspath(sys.argv[1])

    start_time = timeit.default_timer()
    calculate_hashes_sha1(dir_path)
    end_time = timeit.default_timer()
    print("Total time to calculate SHA1 hashes: {0} seconds".format(round(end_time - start_time, NDIGITS_ROUNDING)))

    start_time = timeit.default_timer()
    calculate_hashes_sha256(dir_path)
    end_time = timeit.default_timer()
    print("Total time to calculate SHA-256 hashes: {0} seconds".format(round(end_time - start_time, NDIGITS_ROUNDING)))

    start_time = timeit.default_timer()
    calculate_hashes_sha512(dir_path)
    end_time = timeit.default_timer()
    print("Total time to calculate SHA-512 hashes: {0} seconds".format(round(end_time - start_time, NDIGITS_ROUNDING)))

    start_time = timeit.default_timer()
    calculate_hashes_blake2b(dir_path)
    end_time = timeit.default_timer()
    print("Total time to calculate Blake2b hashes: {0} seconds".format(round(end_time - start_time, NDIGITS_ROUNDING)))
