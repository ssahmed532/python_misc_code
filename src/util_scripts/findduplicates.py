import logging
import os
import pprint
import sys
from collections import defaultdict
from timeit import default_timer as timer
from tqdm import tqdm

import fileutils
import hashutils

# References:
#       https://stackoverflow.com/questions/7370801/measure-time-elapsed-in-python
#       https://stackoverflow.com/questions/14996453/python-libraries-to-calculate-human-readable-filesize-from-bytes
#


#
# TODO:
#
#   - Convert this code into a Class
#   - Add intelligent caching of file hashes: write file hashes to a
#     disk cache; read this cache at startup and invalidate those file hashes
#     for which the file has been modified after the hash creation time
#   - Track cache hits, cache misses, and cache invalidations
#   - DONE - Add support for scanning multiple directories
#     for duplicates among all those directories
#   - DONE - Show a progress bar - using tqdm
#

SUFFIXES = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.info('Logging initialized')


# XXXI: move this function to a new myutils.py module
def humansize(nbytes):
    if nbytes == 0:
        return '0 B'

    i = 0
    while nbytes >= 1024 and i < len(SUFFIXES)-1:
        nbytes /= 1024.0
        i += 1

    f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
    return '{} {}'.format(f, SUFFIXES[i])


# XXXI: move this function to the fileutils.py module
def calcDuplicatesDiskSpace(dupsFileList):
    diskSpaceBytes = 0

    # skip the first file in the duplicates file list as that is the
    # 'first' instance of the file - the remaining instances are all
    # duplicates.
    for dupFile in dupsFileList[1:]:
        diskSpaceBytes += os.path.getsize(dupFile)

    return diskSpaceBytes


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('Usage: python findduplicates.py <dirPath1 dirPath2 ... dirPathN>', file=sys.stderr)
        sys.exit(1)

    dirsList = sys.argv[1:]

    filesList = []

    startTime = timer()
    logging.info('Building files list ...')
    for dir in dirsList:
        files = fileutils.getAllFilesRecursive(dir)
        filesList.extend(files)

    endTime = timer()
    elapsedTime = round(endTime - startTime, 5)
    logging.info('{} files found in {} seconds'.format(len(filesList), elapsedTime))

    fileHashDict = defaultdict(list)
    # number of duplicates detected
    duplicates = 0
    # total disk space occupied by the duplicate files
    duplicatesDiskSpace = 0

    logging.info('Calculating file hashes...')
    startTime = timer()
    for file in tqdm(filesList):
        try:
            fileHash = hashutils.computeFileHashSHA256(file)

            fileHashDict[fileHash].append(file)
        except (PermissionError, FileNotFoundError):
            logging.error('Skipping file {} due to permissions and/or access issues'.format(file))
    print()

    endTime = timer()
    elapsedTime = round(endTime - startTime, 5)

    logging.info('Checking for duplicates...')
    for fileHash in fileHashDict.keys():
        filesList = fileHashDict[fileHash]
        if len(filesList) > 1:
            duplicates += len(filesList) - 1
            duplicatesDiskSpace += calcDuplicatesDiskSpace(filesList)
            print('{} hash for {} different files:'.format(fileHash, len(filesList)))

            # determine the max width to set for pretty printing
            # based on the max. file path length for each list of
            # duplicates for the same hash
            maxWidth = len(max(filesList, key=len))
            pprint.pprint(filesList, width=maxWidth*1.333)
            print()

    if duplicates > 0:
        logging.info('Found {} duplicate files in {} seconds'.format(duplicates, elapsedTime))
        logging.info('Total disk space occupied by duplicate files: {}'.format(humansize(duplicatesDiskSpace)))
    else:
        logging.info('No duplicates found')
