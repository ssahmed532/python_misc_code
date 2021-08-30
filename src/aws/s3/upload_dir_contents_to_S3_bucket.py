import boto3
import os
import sys
import hashlib

from tqdm import tqdm
from botocore.retries import bucket

import s3_utils

# TODO
#   - convert this into a Class
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
#   - add total elapsed time logging
#


def get_crypto_hash(file_path: str) -> str:
    file_hash = ""

    with open(file_path, "rb") as f:
        hash_algo = hashlib.blake2b()
        while chunk := f.read(8192):
            hash_algo.update(chunk)

    file_hash = hash_algo.hexdigest()
    return file_hash


def _upload_file_to_s3_bucket(s3_resource, file_path: str, bucket_name: str, calc_hash: bool) -> bool:
    success = True

    real_path = os.path.realpath(file_path)
    filename = os.path.basename(real_path)

    s3_resource.Bucket(bucket_name).upload_file(Filename=real_path, Key=filename)

    if calc_hash:
        file_hash = get_crypto_hash(real_path)

        # TODO: the following line should only be printed when in verbose mode
        #print(f'[{filename}] -> {file_hash}')

        file_hash_filename = real_path + ".hash"
        try:
            with open(file_hash_filename, "w+") as f:
                f.write("{} {}\n".format(filename, file_hash))

            s3_resource.Bucket(bucket_name).upload_file(Filename=real_path + ".hash", Key=filename + ".hash")
        except:
            print(f'ERROR: unable to write integrity hash to file {file_hash_filename}')

        # TODO: move this file deletion step to the above try ... except block
        try:
            os.remove(file_hash_filename)
        except:
            print(f'ERROR: unable to delete crypto hash file {file_hash_filename}')

    return success


def upload_dir_contents_to_s3_bucket(s3_resource, dir_path: str, bucket_name: str) -> int:
    files_uploaded = 0

    # Iterate over all files in the specified directory and upload them
    # to this S3 bucket
    # TODO: replace os.walk() with os.scandir()
    for subdir, dirs, files in os.walk(dir_path):
        for filename in (progress_bar := tqdm(files, desc='Uploading files')):
            file_path = subdir + os.sep + filename
            _upload_file_to_s3_bucket(s3_resource, file_path, bucket_name, True)
            files_uploaded += 1
            progress_bar.write(filename)

    return files_uploaded


def upload_file_to_s3_bucket(s3_resource, file_path: str, bucket_name: str) -> None:
    _upload_file_to_s3_bucket(s3_resource, file_path, bucket_name, True)


def main(dir_path: str, s3_bucket_name: str, is_file: bool) -> None:
    s3_resource = boto3.resource('s3')

    if not s3_utils.check_bucket(s3_resource, s3_bucket_name):
        print(f'ERROR: cannot upload file(s) to non-existent S3 bucket ({s3_bucket_name})')
    else:
        if is_file:
            upload_file_to_s3_bucket(s3_resource, dir_path, s3_bucket_name)
        else:
            files_uploaded = upload_dir_contents_to_s3_bucket(s3_resource, dir_path, s3_bucket_name)
            print(f'{files_uploaded} files uploaded successfully')


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
