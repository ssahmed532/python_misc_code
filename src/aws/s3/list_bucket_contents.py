import boto3
import sys
import s3_utils


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
