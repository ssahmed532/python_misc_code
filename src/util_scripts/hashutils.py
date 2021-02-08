import hashlib

# References:
#       https://stackoverflow.com/questions/22058048/hashing-a-file-in-python
#       https://stackoverflow.com/questions/1131220/get-md5-hash-of-big-files-in-python
#
#

BLOCKSIZE = 65526


def computeFileHashSHA1(filePath):
    hasher = hashlib.sha1()

    with open(filePath, 'rb') as f:
        while True:
            data = f.read(BLOCKSIZE)
            if not data:
                break

            hasher.update(data)

    return hasher.hexdigest()


def computeFileHashSHA256(filePath):
    hasher = hashlib.sha256()

    with open(filePath, 'rb') as f:
        while True:
            data = f.read(BLOCKSIZE)
            if not data:
                break

            hasher.update(data)

    return hasher.hexdigest()


def computeFileHashSHA512(filePath):
    hasher = hashlib.sha512()

    with open(filePath, 'rb') as f:
        while True:
            data = f.read(BLOCKSIZE)
            if not data:
                break

            hasher.update(data)

    return hasher.hexdigest()
