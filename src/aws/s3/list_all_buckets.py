import argparse
import boto3
import sys
import uuid
from pprint import pprint
from botocore.exceptions import NoCredentialsError


def list_all_s3_buckets(verbose: bool) -> None:
    """List all S3 buckets associated with the current AWS credentials
       and Region, and print to stdout.
    """

    if verbose:
        print(f'boto3 library version is {boto3.__version__}')
        print(f'Current region is {boto3.Session().region_name}')
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

    try:
        list_all_s3_buckets(args.verbose)
    except NoCredentialsError as e:
        print(f'ERROR: Unable to locate AWS credentials or credentials have been setup incorrectly', file=sys.stderr)
