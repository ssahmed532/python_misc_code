import boto3
import uuid
import pprint
import sys


# TODO:
#   - integrate the argparse module
#   - allow for buckets to be created in regions other than the current
#     default region set in aws CLI configuration
#   - bucket creation methods should be moved into the s3_utils module
#   - add a new method to allow creating a bucket by adding the default
#     (or user-specified) prefix to an existing directory name. This will
#     be helpful when uploading a whole directory to a new bucket that will
#     be automatically created prior to uploading the directory.
#


# TODO:
#   - move this to s3_utils module
DEFAULT_BUCKET_PREFIX = 'ssahmed'


def get_new_bucket_name(bucket_prefix):
    return '-'.join([bucket_prefix, str(uuid.uuid4())])


def create_bucket(bucket_name: str, s3_resource):
    session = boto3.session.Session()
    current_region = session.region_name
    #current_region = 'me-south-1'

    if not bucket_name:
        # if the bucket name is not specified then auto-generate one
        bucket_name = get_new_bucket_name(DEFAULT_BUCKET_PREFIX)
        print(f'Auto-generated bucket name is: \"{bucket_name}\"')

    print(f'Creating new bucket \"{bucket_name}\" in region \"{current_region}\"')

    s3_connection = s3_resource.meta.client

    if current_region == 'us-east-1':
        # this has to be done due to a long standing issue in the boto3 library
        #   https://github.com/boto/boto3/issues/125
        bucket_response = s3_connection.create_bucket(Bucket=bucket_name)
    else:
        bucket_response = s3_connection.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={'LocationConstraint': current_region})

    # enable Server-side Encryption at the Bucket level
    # reference:
    #   https://stackoverflow.com/questions/59218289/s3-default-server-side-encryption-on-large-number-of-buckets-using-python-boto3
    response = s3_connection.put_bucket_encryption(
        Bucket=bucket_name,
        ServerSideEncryptionConfiguration={
            'Rules': [
                {
                    'ApplyServerSideEncryptionByDefault': {'SSEAlgorithm': 'AES256'}
                },
            ]
        })

    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        print(f'Server-side Encryption successfully enabled for bucket {bucket_name}')
    else:
        print(f'WARNING: failed to enable Server-side Encryption for bucket {bucket_name}')
        pprint.pprint(response, width=1)

    return bucket_name, bucket_response


def main(s3_bucket_name: str) -> None:
    s3_resource = boto3.resource('s3')

    s3_bucket_name, create_bucket_response = create_bucket(s3_bucket_name, s3_resource)

    if create_bucket_response['ResponseMetadata']['HTTPStatusCode'] == 200:
        print('S3 bucket created successfully')

    print("Name of newly created S3 bucket: " + s3_bucket_name)

    # TODO
    #   add a --verbose flag that prints out the full create_bucket response
    #print("create_bucket response:" )
    #pprint.pprint(create_bucket_response, width=1)


def print_usage_and_exit() -> None:
    print(f'Usage: {sys.argv[0]} [S3 bucket name]', file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    s3_bucket_name = None

    arg_count = len(sys.argv)
    if arg_count == 2:
        if sys.argv[1] == '--help':
            print_usage_and_exit()
        else:
            s3_bucket_name = sys.argv[1]
    elif arg_count > 2:
        print_usage_and_exit()

    main(s3_bucket_name)
