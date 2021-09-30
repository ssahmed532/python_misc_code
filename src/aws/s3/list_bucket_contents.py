import boto3
import sys
import s3_utils


# TODO:
#   - for buckets that reside in a location other than the current
#     default / session region, automatically figure out where that
#     Bucket resides and then specify the LocationConstraint so that
#     we don't get the following sorts of Exceptions:
#
#       botocore.exceptions.ClientError: An error occurred (IllegalLocationConstraintException)
#       when calling the ListObjects operation: The unspecified location constraint is
#       incompatible for the region specific endpoint this request was sent to.
#


def main(bucket_name: str) -> None:
    s3 = boto3.resource('s3')

    bucket_contents = s3_utils.get_bucket_contents(s3, bucket_name)
    for item in bucket_contents:
        print(item)


if __name__ == "__main__":
    if (len(sys.argv) != 2):
        print(f'Usage: {sys.argv[0]} <S3 bucket name>', file=sys.stderr)
        sys.exit(1)

    bucket_name = sys.argv[1]

    main(bucket_name)
