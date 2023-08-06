"""
Most often used interactions with S3

- create bucket name
- create bucket
- list bucket
- list objects in bucket
- delete objects in bucket
- delete bucket
- copy files from one bucket to another

"""
import uuid
from boto3 import resource
from boto3.session import Session
from logdecoratorandhandler.log_decorator import LogDecorator
#
# from config import get_s3_resource


@LogDecorator('INFO - create bucket name')
def create_bucket_name(bucket_prefix='bkt-dfl-app-', bucket_suffix=None) -> str:
    """
    The generated bucket name must be between 3 and 63 chars long.
    Add an uuid to make it unique.
    """
    if bucket_suffix is None:
        return f'{bucket_prefix}{str(uuid.uuid4())}'
    return f'{bucket_prefix}{bucket_suffix}'


@LogDecorator('INFO - create new bucket')
def create_new_bucket(s3: resource, bucket_name: str) -> Session:
    """
    Create bucket with session.
    """
    session = Session()
    current_region = session.region_name
    return s3.create_bucket(Bucket=bucket_name,
                            CreateBucketConfiguration={
                                'LocationConstraint': current_region}
                            )


@LogDecorator('INFO - list objects')
def list_bucket_objects(s3: resource, bucket_name: str) -> list:
    """
    List all objects in bucket.
    """
    bkt = s3.Bucket(bucket_name)
    print(f'List of objects in {bkt}: ')
    object_list = []
    for obj in bkt.objects.all():
        object_list.append(obj.key)
    return object_list


@LogDecorator('INFO - list buckets')
def list_buckets(s3: resource) -> list:
    """
    List all the buckets of user.
    """
    print('List of buckets: ')
    bucket_list = []
    for bkt in s3.buckets.all():
        bucket_list.append(bkt.name)
    return bucket_list


@LogDecorator('INFO - delete objects in bucket')
def delete_bucket_objects(s3: resource, bucket_name: str) -> None:
    """
    Delete all objects in bucket.
    """
    bkt = s3.Bucket(bucket_name)

    objects_list = [{'Key': obj.key} for obj in bkt.objects.all()]
    bkt.delete_objects(Delete={'Objects': objects_list})


@LogDecorator('INFO - delete objects and bucket')
def delete_all(s3: resource, bucket_name: str) -> None:
    """
    Delete all files and bucket.

    If file is too big or there are too much versions, use the bash script:
    delete_versioned_buckets.sh in terminal:
    >> bash delete_versioned_buckets.sh bucket_name
    """
    res = []
    bkt = s3.Bucket(bucket_name)

    for obj in bkt.objects.all():
        res.append({'Key': obj.key})

    if len(res) > 0:
        bkt.delete_objects(Delete={'Objects': res})
    bkt.delete()


@LogDecorator('INFO - delete objects and bucket')
def delete_all_versions(s3: resource, bucket_name: str) -> None:
    """
    Delete all files and bucket.

    If file is too big or there are too much versions, use the bash script:
    delete_versioned_buckets.sh in terminal:
    >> bash delete_versioned_buckets.sh bucket_name
    """
    res = []
    bkt = s3.Bucket(bucket_name)

    for obj_version in bkt.object_versions.all():
        res.append({'Key': obj_version.object_key,
                    'VersionId': obj_version.id})

    if len(res) > 0:
        bkt.delete_objects(Delete={'Objects': res})
    bkt.delete()


@LogDecorator('INFO - copy objects to other bucket')
def copying_between_buckets(s3, source, target):
    """
    For renaming a bucket, you have to copy all files to the new one and
    then delete the old bucket.
    """
    for file in s3.Bucket(name=source).objects.all():
        copy_src = {'Bucket': source, 'Key': file.key}
        s3.Bucket(name=target).copy(copy_src, Key=file.key)
