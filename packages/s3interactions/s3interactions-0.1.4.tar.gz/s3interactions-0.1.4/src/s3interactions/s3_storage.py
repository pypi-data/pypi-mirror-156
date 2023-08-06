"""
S3Storage

- upload files from folder to bucket
- upload single file from folder to bucket

"""
from dataclasses import dataclass, field
from os import listdir
from os.path import isfile, join
from pathlib import Path
from typing import Any

from boto3 import resource
from logdecoratorandhandler.log_decorator import LogDecorator


@dataclass
class S3Storage:
    """
    For uploading data to bucket.
    """
    s3: resource
    bucket_name: str
    in_memory_file: Any = field(default=None)

    @LogDecorator('INFO - upload single file to bucket')
    def upload_single_file(self, f_name: str, f_path: str = None) -> None:
        """
        Upload a single file to bucket:

        - from folder
        - in memory:
            in_memory_file = BytesIO()
            content.save_as(in_memory_file, write_like_original=False)
        """
        obj = self.s3.Object(bucket_name=self.bucket_name,
                             key=f_name)

        if self.in_memory_file is None:
            obj.upload_file(Filename=str(Path(f_path, f_name)))
        else:
            bkt = self.s3.Bucket(self.bucket_name)
            bkt.put_object(Body=self.in_memory_file, Key=f_name)

    @LogDecorator('INFO - upload files from folder to bucket')
    def upload_from_folder(self, f_path: str) -> None:
        """
        Upload all files from folder to bucket.
        """
        for file in get_file_names(f_path):
            self.upload_single_file(file, f_path)

    @LogDecorator('INFO - upload files from folder to bucket')
    def upload_zip(self, zip_file: str) -> None:
        """
        Upload all files from folder to bucket.
        """
        obj = self.s3.Object(bucket_name=self.bucket_name,
                             key=zip_file)
        obj.upload_file(Filename=zip_file)


@LogDecorator('INFO - get log infos as list')
def get_file_names(file_path):
    """Get file names of directory."""
    return [f for f in listdir(file_path) if isfile(join(file_path, f))]



# zip_bytes_io = io.BytesIO()
# zip_archive = zipfile.ZipFile(zip_bytes_io, mode='a',
#                               compression=zipfile.ZIP_DEFLATED)
# zip_archive.writestr('test.txt', b'My string')
# s3_client = boto3.client('s3')
# zip_bytes_io.seek(0)  # So that bytes are read from beginning
# s3_client.upload_fileobj(zip_bytes_io, test_bucket, 'test.zip')
