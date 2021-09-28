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
