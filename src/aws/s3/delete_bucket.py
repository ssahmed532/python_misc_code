import argparse
import boto3
import pprint
import sys

import commons
import s3_utils

from botocore.exceptions import ClientError

# TODO
#   - add an interactive prompt that checks whether the user really
#     wants to delete the specified bucket
#   - handle non-empty buckets by prompting the user once more and then
#     iteratively delete all of the objects in the bucket before
#     deleting the bucket itself.
#


def delete_bucket(bucket_name: str, verbose: bool) -> bool:
    if verbose:
        print(f'boto3 library version is {boto3.__version__}')
        print(f'Current region is {boto3.Session().region_name}')
        print()

    bucket_location = s3_utils.get_bucket_location(bucket_name)

    try:
        print(f'Deleting S3 bucket {bucket_name} in location {bucket_location} ...')

        s3_client = boto3.client('s3', region_name=bucket_location)
        response = s3_client.delete_bucket(Bucket=bucket_name)

        if verbose:
            print('delete_bucket() response:')
            pprint.pprint(response)
            print()

        if response['ResponseMetadata']['HTTPStatusCode'] == 204:
            print(f'S3 bucket {bucket_name} successfully deleted')
            return True
    except ClientError as e:
        print(f'S3 client error occurred while trying to delete bucket:')
        print(f"\tError Code: {e.response['Error']['Code']}")
        print(f"\tError Msg:  {e.response['Error']['Message']}")
        return False


def user_confirm() -> bool:
    answer = ""

    while answer not in ["y", "yes", "n", "no"]:
        answer = input("Are you sure you want to delete the S3 bucket? [Y/N] ").lower()

    return (answer == "y") or (answer == "yes")


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(
        description='Script to delete an existing S3 Bucket')

    arg_parser.add_argument(
        "-v",
        "--verbose",
        required=False,
        action="store_true",
        help="display verbose output"
        )

    arg_parser.add_argument(
        's3_bucket_name',
        type=str,
        help='name of the S3 Bucket'
        )

    arg_parser.add_argument(
        "-y",
        "--yes",
        required=False,
        action="store_true",
        help="assume Yes to all confirmation prompts"
        )

    args = arg_parser.parse_args()

    no_user_prompt = args.yes

    if no_user_prompt:
        print(f'WARNING: proceeding with deleting S3 bucket {args.s3_bucket_name} without prompt/confirmation ...')
        delete_bucket(bucket_name=args.s3_bucket_name, verbose=args.verbose)
    else:
        if user_confirm():
            delete_bucket(bucket_name=args.s3_bucket_name, verbose=args.verbose)
