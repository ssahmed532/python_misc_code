import boto3
import botocore


# taken from:
#   https://stackoverflow.com/questions/26871884/how-can-i-easily-determine-if-a-boto-3-s3-bucket-resource-exists
def check_bucket(s3_resource, bucket_name):
    try:
        s3_resource.meta.client.head_bucket(Bucket=bucket_name)
        return True
    except botocore.exceptions.ClientError as e:
        print("Bucket named {} does NOT exist".format(bucket_name))
        return False
