import boto3
import uuid
import pprint


def main():
    print(f'boto3 library version is: {boto3.__version__}')
    print()

    # TODO: move this into a utility function in s3_utils

    # Retrieve the list of existing buckets
    s3 = boto3.client('s3')
    response = s3.list_buckets()

    # Output the bucket names
    print('Existing buckets:')
    for bucket in response['Buckets']:
        print(f'    {bucket["Name"]} created on {bucket["CreationDate"]}')


if __name__ == "__main__":
    main()
