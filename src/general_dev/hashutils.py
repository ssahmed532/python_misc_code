import hashlib

# References:
#       https://stackoverflow.com/questions/22058048/hashing-a-file-in-python
#       https://stackoverflow.com/questions/1131220/get-md5-hash-of-big-files-in-python
#       https://stackoverflow.com/questions/16874598/how-do-i-calculate-the-md5-checksum-of-a-file-in-python
#

BLOCK_SIZE = (65 * 1024)


def computeFileHashSHA1(file_path):
    with open(file_path, 'rb') as f:
        hasher = hashlib.sha1()

        while chunk := f.read(BLOCK_SIZE):
            hasher.update(chunk)

    return hasher.hexdigest()


def computeFileHashSHA256(file_path):
    with open(file_path, 'rb') as f:
        hasher = hashlib.sha256()

        while chunk := f.read(BLOCK_SIZE):
            hasher.update(chunk)

    return hasher.hexdigest()


def computeFileHashSHA512(file_path):
    with open(file_path, 'rb') as f:
        hasher = hashlib.sha512()

        while chunk := f.read(BLOCK_SIZE):
            hasher.update(chunk)

    return hasher.hexdigest()


def computeFileHashBlake2b(file_path):
    hasher = hashlib.blake2b()

    with open(file_path, 'rb') as f:
        while chunk := f.read(BLOCK_SIZE):
            hasher.update(chunk)

    return hasher.hexdigest()
