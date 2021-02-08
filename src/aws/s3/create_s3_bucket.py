import boto3
import uuid
import pprint


def get_new_bucket_name(bucket_prefix):
    return '-'.join([bucket_prefix, str(uuid.uuid4())])


def create_bucket(bucket_prefix, s3_resource):
    session = boto3.session.Session()
    current_region = session.region_name
    print(current_region)
    bucket_name = get_new_bucket_name(bucket_prefix)

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
        print('Server-side Encryption successfully enabled for bucket')
    else:
        print('WARNING: failed to enable Server-side Encryption for bucket: ' + bucket_name)
        pprint.pprint(response, width=1)

    print(bucket_name, current_region)
    return bucket_name, bucket_response


def main():
    s3_resource = boto3.resource('s3')

    s3_bucket_name, create_bucket_response = create_bucket('ssahmed', s3_resource)

    print("Name of newly created S3 bucket: " + s3_bucket_name)
    print("create_bucket response:" )
    pprint.pprint(create_bucket_response, width=1)


if __name__ == "__main__":
    main()
