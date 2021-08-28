import boto3
import os
import sys
import hashlib

import s3_utils

PDF_EXT = '.pdf'



def get_crypto_hash(file_path: str) -> str:
    file_hash = ""

    with open(file_path, "rb") as f:
        hash_algo = hashlib.blake2b()
        while chunk := f.read(8192):
            hash_algo.update(chunk)

    file_hash = hash_algo.hexdigest()
    return file_hash




def _upload_file_to_s3_bucket(s3_resource, file_path: str, bucket_name: str, calc_hash: bool) -> bool:
    success = True

    real_path = os.path.realpath(file_path)
    filename = os.path.basename(real_path)

    print(f'Uploading file [{real_path}] to bucket [{bucket_name}] ... ', end='')
    s3_resource.Bucket(bucket_name).upload_file(Filename=real_path, Key=filename)
    print('OK.')

    if calc_hash:
        file_hash = get_crypto_hash(real_path)
        print(f'Integrity hash of [{real_path}] is {file_hash}')

        file_hash_filename = real_path + ".hash"
        try:
            with open(file_hash_filename, "w+") as f:
                f.write("{} {}\n".format(filename, file_hash))

            s3_resource.Bucket(bucket_name).upload_file(Filename=real_path + ".hash", Key=filename + ".hash")
        except:
            print(f'ERROR: unable to write integrity hash to file {file_hash_filename}')

        # TODO
        # move this file deletion step to the above try ... except block
        try:
            os.remove(file_hash_filename)
        except:
            print(f'ERROR: unable to delete crypto hash file {file_hash_filename}')

    return success


def upload_dir_contents_to_s3_bucket(dir_path: str, bucket_name: str) -> None:
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


def upload_file_to_s3_bucket(file_path: str, bucket_name: str) -> None:
    s3_resource = boto3.resource('s3')

    if s3_utils.check_bucket(s3_resource, bucket_name):
        _upload_file_to_s3_bucket(s3_resource, file_path, bucket_name, True)
    else:
        print(f'ERROR: cannot upload files to non-existent bucket ({bucket_name})')


def main(dir_path: str, s3_bucket_name: str, is_file: bool) -> None:
    if is_file:
        upload_file_to_s3_bucket(dir_path, s3_bucket_name)
    else:
        upload_dir_contents_to_s3_bucket(dir_path, s3_bucket_name)


if __name__ == "__main__":
    if (len(sys.argv) < 3):
        print(f'Usage: {sys.argv[0]} <directory path> <S3 bucket name>', file=sys.stderr)
        sys.exit(1)

    fs_path = sys.argv[1]

    is_file = os.path.isfile(fs_path)

    if not is_file and not os.path.isdir(fs_path):
        print(f'ERROR: invalid or non-existent path {fs_path} to upload to AWS S3 bucket', file=sys.stderr)
        sys.exit(1)

    main(fs_path, sys.argv[2], is_file)
