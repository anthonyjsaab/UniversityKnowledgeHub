"""
THIS FILE IS NOT A VIEWS FILE
It contains conventional Python functions that uses Boto3
"""
import boto3
from botocore.config import Config
from UniversityKnowledgeHub import settings


def s3_generate_down_url(object_name, expiry_seconds):
    s3 = boto3.client('s3', config=Config(signature_version=settings.AWS_S3_SIGNATURE_VERSION,
                                          region_name=settings.AWS_S3_REGION_NAME))
    url = s3.generate_presigned_url('get_object',
                                    Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                                            'Key': object_name},
                                    ExpiresIn=expiry_seconds)
    return url


def s3_upload_file(path, object_name):
    s3 = boto3.client('s3')
    s3.upload_file(path, settings.AWS_STORAGE_BUCKET_NAME, object_name)


def s3_upload_fileobj(obj, object_name):
    s3 = boto3.client('s3')
    s3.upload_fileobj(obj, settings.AWS_STORAGE_BUCKET_NAME, object_name)

