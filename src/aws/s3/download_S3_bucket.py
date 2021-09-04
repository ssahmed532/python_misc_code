import boto3
import os
import sys
import s3_utils

from datetime import timedelta
from timeit import default_timer as timer
from tqdm import tqdm


class S3FileDownloader:
    """A utility class to download files from an S3 Bucket
    """

    def __init__(self, bucket_name: str) -> None:
        self.bucket_name = bucket_name
        self.s3_resource = None


    def initialize(self) -> None:
        resource = boto3.resource('s3')

        if not s3_utils.check_bucket(resource, self.bucket_name):
            # TODO: raise an appropriate Exception here
            print(f'ERROR: cannot download files from a non-existent S3 bucket ({self.bucket_name})')
        else:
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

        return files_downloaded


def main(s3_bucket_name: str) -> None:
    file_downloader = S3FileDownloader(s3_bucket_name)
    file_downloader.initialize()

    start = timer()
    count = file_downloader.download_all_files()
    end = timer()

    elapsed_time = round(end - start, 3)
    print(f'Downloaded {count} files in time: {elapsed_time} seconds')


if __name__ == "__main__":
    if (len(sys.argv) != 2):
        print(f'Usage: {sys.argv[0]} <S3 bucket name>', file=sys.stderr)
        sys.exit(1)

    bucket_name = sys.argv[1]

    main(bucket_name)
