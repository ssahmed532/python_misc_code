import hashlib

# References:
#       https://stackoverflow.com/questions/22058048/hashing-a-file-in-python
#       https://stackoverflow.com/questions/1131220/get-md5-hash-of-big-files-in-python
#       https://stackoverflow.com/questions/16874598/how-do-i-calculate-the-md5-checksum-of-a-file-in-python
#

BLOCK_SIZE = 65 * 1024


def calc_file_hash_SHA1(file_path: str) -> str:
    with open(file_path, "rb") as f:
        hasher = hashlib.sha1()

        while chunk := f.read(BLOCK_SIZE):
            hasher.update(chunk)

    return hasher.hexdigest()


def calc_file_hash_SHA256(file_path: str) -> str:
    with open(file_path, "rb") as f:
        hasher = hashlib.sha256()

        while chunk := f.read(BLOCK_SIZE):
            hasher.update(chunk)

    return hasher.hexdigest()


def calc_file_hash_SHA512(file_path: str) -> str:
    with open(file_path, "rb") as f:
        hasher = hashlib.sha512()

        while chunk := f.read(BLOCK_SIZE):
            hasher.update(chunk)

    return hasher.hexdigest()


def calc_file_hash_Blake2b(file_path: str) -> str:
    hasher = hashlib.blake2b()

    with open(file_path, "rb") as f:
        while chunk := f.read(BLOCK_SIZE):
            hasher.update(chunk)

    return hasher.hexdigest()


def calc_file_hash_SHA3_256(file_path: str) -> str:
    hasher = hashlib.sha3_256()

    with open(file_path, "rb") as f:
        while chunk := f.read(BLOCK_SIZE):
            hasher.update(chunk)

    return hasher.hexdigest()


def calc_str_hash_SHA1(data: str) -> str:
    hasher = hashlib.sha1()

    hasher.update(data.encode("utf-8"))

    return hasher.hexdigest()


def calc_str_hash_SHA224(data: str) -> str:
    hasher = hashlib.sha224()

    hasher.update(data.encode("utf-8"))

    return hasher.hexdigest()


def calc_str_hash_SHA256(data: str) -> str:
    hasher = hashlib.sha256()

    hasher.update(data.encode("utf-8"))

    return hasher.hexdigest()


def calc_str_hash_SHA384(data: str) -> str:
    hasher = hashlib.sha384()

    hasher.update(data.encode("utf-8"))

    return hasher.hexdigest()


def calc_str_hash_SHA512(data: str) -> str:
    hasher = hashlib.sha512()

    hasher.update(data.encode("utf-8"))

    return hasher.hexdigest()


def calc_str_hash_Blake2b(data: str) -> str:
    hasher = hashlib.blake2b()

    hasher.update(data.encode("utf-8"))

    return hasher.hexdigest()


def calc_str_hash_SHA3_512(data: str) -> str:
    hasher = hashlib.sha3_512()

    hasher.update(data.encode("utf-8"))

    return hasher.hexdigest()
