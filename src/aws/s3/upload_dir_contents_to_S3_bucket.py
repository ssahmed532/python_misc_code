import boto3
import os
import sys
import hashlib

from datetime import timedelta
from timeit import default_timer as timer
from tqdm import tqdm
from botocore.retries import bucket

import s3_utils

# TODO
#   - integrate the argparse module
#   - integrate the Python std logging module, and log all output to
#     an ondisk logfile
#   - add an option for auto-creating an S3 bucket based on a user-specified
#     bucket prefix
#   - when uploading the contents of an entire directory, generate a manifest
#     file that lists all of the files and their respective hashes
#   - prompt when a file with the same key already exists in the target bucket
#   - add a verbose mode
#   - add an option to recurse into all sub-directories when uploading files. If not specified,
#     only upload those files in the root of the specified directory.
#   - add an option to skip (cryptographic) hash generation
#   - add an option to only upload a certain type of files (e.g. only PDFs, only .txt files, etc)
#   - [DONE] convert this into a Class
#   - [DONE] add total elapsed time logging
#


def get_crypto_hash(file_path: str) -> str:
    file_hash = ""

    with open(file_path, "rb") as f:
        hash_algo = hashlib.blake2b()
        while chunk := f.read(8192):
            hash_algo.update(chunk)

    file_hash = hash_algo.hexdigest()
    return file_hash


class S3FileUploader:
    """A utility class to upload files to an existing S3 Bucket
    """

    def __init__(self, bucket_name: str) -> None:
        self.bucket_name = bucket_name
        self.s3_resource = None


    def initialize(self) -> None:
        resource = boto3.resource('s3')

        if not s3_utils.check_bucket(resource, self.bucket_name):
            # TODO: raise an appropriate Exception here
            print(f'ERROR: cannot upload file(s) to non-existent S3 bucket ({self.bucket_name})')
        else:
            self.s3_resource = resource


    def _upload_file_to_s3_bucket(self, file_path: str, calc_hash: bool) -> bool:
        """Upload specified file to S3 bucket (internal helper)

        Args:
            file_path (str): full path to file to be uploaded
            calc_hash (bool): if True, compute the integrity hash for the file

        Returns:
            bool: True if file was uploaded successfully
        """
        success = True

        real_path = os.path.realpath(file_path)
        filename = os.path.basename(real_path)

        self.s3_resource.Bucket(self.bucket_name).upload_file(Filename=real_path, Key=filename)

        if calc_hash:
            file_hash = get_crypto_hash(real_path)

            # TODO: the following line should only be printed when in verbose mode
            #print(f'[{filename}] -> {file_hash}')

            file_hash_filename = real_path + ".hash"
            try:
                with open(file_hash_filename, "w+") as f:
                    f.write("{} {}\n".format(filename, file_hash))

                self.s3_resource.Bucket(self.bucket_name).upload_file(Filename=real_path + ".hash", Key=filename + ".hash")
            except:
                print(f'ERROR: unable to write integrity hash to file {file_hash_filename}')

            # TODO: move this file deletion step to the above try ... except block
            try:
                os.remove(file_hash_filename)
            except:
                print(f'ERROR: unable to delete crypto hash file {file_hash_filename}')

        return success


    def upload_dir_contents(self, dir_path: str) -> int:
        """Upload all of the files contained in a directory to the S3 bucket

        Args:
            dir_path (str): full path to the directory

        Returns:
            int: number of files successfully uploaded
        """
        files_uploaded = 0

        # Iterate over all files in the specified directory and upload
        # them to this S3 bucket
        # TODO: replace os.walk() with os.scandir()
        for subdir, dirs, files in os.walk(dir_path):
            for filename in (progress_bar := tqdm(files, desc='Uploading files')):
                file_path = subdir + os.sep + filename
                self._upload_file_to_s3_bucket(file_path, True)
                files_uploaded += 1
                progress_bar.write(filename)

        return files_uploaded


    def upload_file(self, file_path: str) -> None:
        """Upload a file to the S3 bucket

        Args:
            file_path (str): full path to the file
        """
        self._upload_file_to_s3_bucket(file_path, True)


def main(dir_path: str, s3_bucket_name: str, is_file: bool) -> None:
    file_uploader = S3FileUploader(s3_bucket_name)
    file_uploader.initialize()

    start = timer()
    if is_file:
        file_uploader.upload_file(dir_path)
    else:
        files_uploaded = file_uploader.upload_dir_contents(dir_path)
        print(f'{files_uploaded} files uploaded successfully')
    end = timer()

    elapsed_time = round(end - start, 3)
    print(f'Elapsed time: {elapsed_time} seconds')


if __name__ == "__main__":
    if (len(sys.argv) < 3):
        print(f'Usage: {sys.argv[0]} <directory path> <S3 bucket name>', file=sys.stderr)
        sys.exit(1)

    fs_path = sys.argv[1]

    is_file = os.path.isfile(fs_path)

    if not is_file and not os.path.isdir(fs_path):
        print(f'ERROR: invalid or non-existent path {fs_path} to upload to AWS S3 bucket', file=sys.stderr)
        sys.exit(1)

    main(fs_path, sys.argv[2], is_file)
