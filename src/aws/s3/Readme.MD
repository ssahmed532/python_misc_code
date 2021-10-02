Prior to running any of the Python scripts in this directory, please be
sure to properly the Boto3 Python library for programmatic access to
AWS resouces using Python:

- Install the latest version of Boto3 release via pip

- Login to the AWS Console and navigate to the IAM section

- Add another IAM user:
	- specify a new, distinct username (e.g. boto3user_other)
	- set AWS access type to 'Access key - Programmatic access'
	- create a new Group named 'S3_Access' with attached (permissions) Policy set to AmazonS3FullAccess
	- set permissions boundary to 'Create user without a permissions boundary'
	- add tags: s3_access (value unset)

- Once this is done, the new IAM user will have been created and its
  associated security credentials will be available on the AWS console
  for use in the application.

- Copy and save the **Access Key ID** and **Secret Access Key** for use in the
  Python application. Ensure to copy and save the **Secret Access Key** in
  a 'safe location' as the Secret access key cannot be retrieved again
  after the previous step.

- Download, install, and setup the AWS CLI (https://aws.amazon.com/cli/)

- From a new Windows command prompt, enter the following commands:
	aws configure
	- enter the **AWS Access Key ID** from the previous step above
	- enter the **AWS Secret Access Key** from the previous step above
	- set the default region to use (e.g. us-east-1 or some such)

- Once this is done, the Python scripts in this directory can be run
  from a Python-enabled command prompt or terminal:
    (e.g.)
    - ``python list_all_buckets.py``    
    - ``python create_s3_bucket.py``    
