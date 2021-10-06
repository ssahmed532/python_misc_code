import boto3
import pprint
import sys

import commons
import s3_utils

from botocore.exceptions import ClientError

# TODO
#   - integrate the argparse module
#   - add an interactive prompt that checks whether the user really
#     wants to delete the specified bucket
#   - handle non-empty buckets by prompting the user once more and then
#     iteratively delete all of the objects in the bucket before
#     deleting the bucket itself.
#


def delete_bucket(bucket_name):
    bucket_location = s3_utils.get_bucket_location(bucket_name)

    try:
        s3_client = boto3.client('s3', region_name=bucket_location)
        response = s3_client.delete_bucket(Bucket=bucket_name)

        if response['ResponseMetadata']['HTTPStatusCode'] == 204:
            print(f'S3 bucket {bucket_name} successfully deleted')
            return True
    except ClientError as e:
        print(f'S3 client error occurred while trying to delete bucket:')
        print(f"\tError Code: {e.response['Error']['Code']}")
        print(f"\tError Msg:  {e.response['Error']['Message']}")
        return False


if __name__ == "__main__":
    if (len(sys.argv) < 2):
        print('Usage: {} <S3 bucket name>'.format(sys.argv[0]), file=sys.stderr)
        sys.exit(1)

    delete_bucket(bucket_name=sys.argv[1])
