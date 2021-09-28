import argparse
import boto3
import uuid
from pprint import pprint


def list_all_buckets(verbose: bool) -> None:
    if verbose:
        print(f'boto3 library version is {boto3.__version__}')
        print()

    # Retrieve the list of existing buckets
    s3 = boto3.client('s3')
    response = s3.list_buckets()

    if verbose:
        print('list_buckets response data:')
        pprint(response)
        print()

    # Output the bucket names
    print('Existing S3 buckets:')
    for index, bucket in enumerate(response['Buckets'], start=1):
        if verbose:
            print(f'    {index}. {bucket["Name"]} created on {bucket["CreationDate"]}')
        else:
            print(f'    {index}. {bucket["Name"]}')
    print()


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(
        description='Script to list all S3 Buckets')

    arg_parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="display verbose output")

    args = arg_parser.parse_args()

    list_all_buckets(args.verbose)
