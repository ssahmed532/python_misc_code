import boto3
import pprint
import sys


def main(bucket_name):
    s3_resource = boto3.resource('s3')

    bucket = s3_resource.Bucket(bucket_name)

    response = bucket.delete()

    print("delete bucket response:" )
    pprint.pprint(response, width=1)


if __name__ == "__main__":
    if (len(sys.argv) < 2):
        print('Usage: {} <S3 bucket name>'.format(sys.argv[0]), file=sys.stderr)
        sys.exit(1)

    main(sys.argv[1])
