
class NonExistentS3BucketError(Exception):
    """Raised when a specific, named S3 Bucket does not exist"""
    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name
        self.message = 'S3 Bucket does not exist'
        super().__init__(self.message)
