import os
import sys
import timeit
import json
import hashlib

import hashutils


NDIGITS_ROUNDING = 4


previous_hashes = {}
current_hashes = {}


def calculate_hashes_sha1(dir_path):
    for filename in os.listdir(dir_path):
        f = os.path.join(dir_path, filename)
        if os.path.isfile(f):
            hash_value = hashutils.computeFileHashSHA1(f)
            current_hashes[filename + "_sha1"] = hash_value


def calculate_hashes_sha256(dir_path):
    for filename in os.listdir(dir_path):
        f = os.path.join(dir_path, filename)
        if os.path.isfile(f):
            hash_value = hashutils.computeFileHashSHA256(f)
            current_hashes[filename + "_sha256"] = hash_value


def calculate_hashes_sha512(dir_path):
    for filename in os.listdir(dir_path):
        f = os.path.join(dir_path, filename)
        if os.path.isfile(f):
            hash_value = hashutils.computeFileHashSHA512(f)
            current_hashes[filename + "_sha512"] = hash_value


def calculate_hashes_blake2b(dir_path):
    for filename in os.listdir(dir_path):
        f = os.path.join(dir_path, filename)
        if os.path.isfile(f):
            hash_value = hashutils.computeFileHashBlake2b(f)
            current_hashes[filename + "_blake2b"] = hash_value

def calculate_hashes_sha3_256(dir_path):
    for filename in os.listdir(dir_path):
        f = os.path.join(dir_path, filename)
        if os.path.isfile(f):
            hash_value = hashutils.computeFileHashSHA3_256(f)
            current_hashes[filename + "_sha3-256"] = hash_value


def write_hash_values(hashes_dict, dir_path, hash_filename):
        output_filename = os.path.join(dir_path, hash_filename)
        with open(output_filename, 'w') as of:
            of.write(json.dumps(hashes_dict)) # use `json.loads` to do the reverse


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('Usage: python benchmark_hash_functions.py <dirPath containing lots of files>', file=sys.stderr)
        sys.exit(1)

    dir_path = os.path.abspath(sys.argv[1])

    print("hashlib hash algorithms available are:")
    print(hashlib.algorithms_available)

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

    start_time = timeit.default_timer()
    calculate_hashes_sha3_256(dir_path)
    end_time = timeit.default_timer()
    print("Total time to calculate SHA3-256 hashes: {0} seconds".format(round(end_time - start_time, NDIGITS_ROUNDING)))

    dir_name =  os.path.basename(os.path.normpath(dir_path))
    write_hash_values(current_hashes, dir_path, dir_name + "_all_hashes.txt")
