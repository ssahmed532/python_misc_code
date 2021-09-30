import boto3
import os
import sys

import hash_utils
import s3_utils

from datetime import timedelta
from timeit import default_timer as timer
from tqdm import tqdm
from commons import NonExistentS3BucketError


# TODO
#   - integrate the argparse module
#   - integrate the Python std logging module, and log all output to
#     an ondisk logfile
#   - by default, this script should download the contents of the bucket
#     into a local dir with the same name as the S3 bucket
#   - if a -d <download dir/path> option is specified, then the contents of the
#     S3 bucket should be downloaded into that specified dir/path
#   - modify this script such that the integrity hash files are an internal
#     implementation detail and nothing about them is visible except for when
#     file integrity verification fails
#   - add a verbose mode
#


class S3FileDownloader:
    """A utility class to download files from an S3 Bucket
    """

    def __init__(self, bucket_name: str) -> None:
        self.bucket_name = bucket_name
        self.s3_resource = None
        self.hash_files = []

    def initialize(self) -> None:
        resource = boto3.resource('s3')

        if not s3_utils.check_bucket(resource, self.bucket_name):
            raise NonExistentS3BucketError(self.bucket_name)

        self.s3_resource = resource

    def download_all_files(self) -> int:
        files_downloaded = 0

        bucket_files = s3_utils.get_bucket_contents(self.s3_resource, self.bucket_name)

        os.mkdir(self.bucket_name)

        for file in (progress_bar := tqdm(bucket_files, desc='Downloading files')):
            full_file_path = os.path.join(self.bucket_name, file)
            self.s3_resource.Bucket(self.bucket_name).download_file(file, full_file_path)
            files_downloaded += 1
            progress_bar.write(full_file_path)
            split_tup = os.path.splitext(full_file_path)
            if split_tup[1] == '.hash':
                self.hash_files.append(full_file_path)

        return files_downloaded

    def verify_hashes(self) -> int:
        print(f'Verifying {len(self.hash_files)} hash files ...')
        for hash_filename in self.hash_files:
            verified = hash_utils.verify_integrity_hash_file(hash_filename)
            if verified:
                print(f'Integrity hash file {hash_filename} is OK')
                os.remove(hash_filename)


def main(s3_bucket_name: str) -> None:
    file_downloader = S3FileDownloader(s3_bucket_name)
    try:
        file_downloader.initialize()
    except NonExistentS3BucketError as e:
        print(f'ERROR: cannot download file(s) from non-existent S3 bucket ({s3_bucket_name})', file=sys.stderr)
        sys.exit(2)

    start = timer()
    count = file_downloader.download_all_files()
    end = timer()

    elapsed_time = round(end - start, 3)
    print(f'Downloaded {count} files in time: {elapsed_time} seconds')

    file_downloader.verify_hashes()


if __name__ == "__main__":
    if (len(sys.argv) != 2):
        print(f'Usage: {sys.argv[0]} <S3 bucket name>', file=sys.stderr)
        sys.exit(1)

    bucket_name = sys.argv[1]

    main(bucket_name)
