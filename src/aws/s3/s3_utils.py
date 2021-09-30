import boto3
import botocore
from boto3.resources.base import ServiceResource


# taken from:
#   https://stackoverflow.com/questions/26871884/how-can-i-easily-determine-if-a-boto-3-s3-bucket-resource-exists
def check_bucket(s3_resource: ServiceResource, bucket_name: str) -> bool:
    try:
        s3_resource.meta.client.head_bucket(Bucket=bucket_name)
        return True
    except botocore.exceptions.ClientError as e:
        return False


def get_bucket_contents(s3_resource: ServiceResource, bucket_name: str) -> list[str]:
    """Get a list of the contents in the specified S3 bucket

    Args:
        s3_resource (ServiceResource): a valid, initialized S3 service resource object
        bucket_name (str): name of the S3 bucket

    Returns:
        list[str]: a list of files in the specified S3 bucket
    """

    bucket_contents = []

    bucket = s3_resource.Bucket(bucket_name)
    for obj in bucket.objects.all():
        bucket_contents.append(obj.key)

    return bucket_contents


def get_bucket_location(s3_client: "botocore.client.S3", bucket_name: str) -> str:
    """Get the location (region) the bucket resides in

    Args:
        s3_client (botocore.client.S3): a valid, initialized low-level S3 client object
        bucket_name (str): name of the S3 bucket

    Returns:
        str: the location (region) the bucket resides in
    """

    location = s3_client.get_bucket_location(Bucket=bucket_name)['LocationConstraint']

    # A peculiarity of the Boto3 library (or of the underlying AWS API)
    # is that Buckets created in region us-east-1 will have a
    # LocationConstraint value of null which in Boto3 is returned as None.
    # The Response dict will have a LocationConstraint key but its value
    # will be None for buckets created in us-east-1.
    #
    # https://stackoverflow.com/questions/67370746/what-does-region-none-mean-when-creating-a-aws-s3-bucket/67370874
    #

    return 'us-east-1' if not location else location
