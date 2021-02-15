import boto3
import os
import sys
import hashlib

import s3_utils

PDF_EXT = '.pdf'



def get_crypto_hash(file_path):
    file_hash = ""

    with open(file_path, "rb") as f:
        hash_algo = hashlib.blake2b()
        while chunk := f.read(8192):
            hash_algo.update(chunk)

    file_hash = hash_algo.hexdigest()
    return file_hash


def upload_dir_contents_to_s3_bucket(dir_path, bucket_name):
    s3_resource = boto3.resource('s3')

    bucket_exists = s3_utils.check_bucket(s3_resource, bucket_name)
    if not bucket_exists:
        print("ERROR: cannot upload files to non-existent bucket ({})".format(bucket_name))
        return
    
    # now that we know that the bucket exists, iterate over all files in
    # the specified directory and upload them to this S3 bucket
    for subdir, dirs, files in os.walk(dir_path):
        for filename in files:
            filepath = subdir + os.sep + filename

            if filepath.endswith(PDF_EXT):
                print(filepath)
                s3_resource.Bucket(bucket_name).upload_file(Filename=filepath, Key=filename)


def upload_file_to_s3_bucket(file_path, bucket_name):
    s3_resource = boto3.resource('s3')

    bucket_exists = s3_utils.check_bucket(s3_resource, bucket_name)
    if not bucket_exists:
        print("ERROR: cannot upload files to non-existent bucket ({})".format(bucket_name))
        return

    real_path = os.path.realpath(file_path)
    filename = os.path.basename(real_path)

    print("Cryptographic hash of [{}] is {}".format(real_path, get_crypto_hash(real_path)))

    crypto_hash = get_crypto_hash(real_path)
    crypto_hash_filename = real_path + ".hash"
    try:
        with open(crypto_hash_filename, "w+") as f:
            f.write("{} {}\n".format(filename, crypto_hash))
    except:
        print("ERROR: unable to write crypto hash to file")

    print("Uploading file [{}] to bucket [{}] ...".format(real_path, bucket_name))
    s3_resource.Bucket(bucket_name).upload_file(Filename=real_path, Key=filename)
    s3_resource.Bucket(bucket_name).upload_file(Filename=real_path + ".hash", Key=filename + ".hash")
    print("DONE.")

    try:
        os.remove(crypto_hash_filename)
    except:
        print("ERROR: unable to delete crypto hash file ", crypto_hash_filename)


def main(dir_path, s3_bucket_name, is_file):
    if is_file:
        upload_file_to_s3_bucket(dir_path, s3_bucket_name)
    else:
        upload_dir_contents_to_s3_bucket(dir_path, s3_bucket_name)


if __name__ == "__main__":
    if (len(sys.argv) < 3):
        print('Usage: {} <directory path> <S3 bucket name>'.format(sys.argv[0]), file=sys.stderr)
        sys.exit(1)

    filesystemPath = sys.argv[1]

    is_file = os.path.isfile(filesystemPath)

    if not is_file and not os.path.isdir(filesystemPath):
        print("ERROR: invalid or non-existent target {} to upload to AWS S3 bucket".format(filesystemPath), file=sys.stderr)
        sys.exit(1)

    main(sys.argv[1], sys.argv[2], is_file)
