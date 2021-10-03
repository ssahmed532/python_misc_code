
class NonExistentS3BucketError(Exception):
    """Raised when a specific, named S3 Bucket does not exist"""
    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name
        self.message = 'S3 Bucket does not exist'
        super().__init__(self.message)


class AwsRegions:
    US_EAST1 = 'us-east-1'
    US_EAST2 = 'us-east-2'
    US_WEST1 = 'us-west-1'
    US_WEST2 = 'us-west-2'
    MIDDLE_EAST1 = 'me-south-1'
    SOUTH_AMERICA1 = 'sa-east-1'
