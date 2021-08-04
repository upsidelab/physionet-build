import os
from django.conf import settings
from google.cloud.exceptions import NotFound
from google.cloud.storage import Client
from storages.backends.gcloud import GoogleCloudStorage
from project.utility import FileInfo, DirectoryInfo, readable_size

# One session per main django process.
# One resource per thread. https://boto3.amazonaws.com/v1/documentation/api/latest/guide/resources.html?highlight=multithreading#multithreading-or-multiprocessing-with-resources

if settings.STORAGE_TYPE == 'S3':
    session = None

def get_client():
    return GoogleCloudStorage().client


class ObjectPath(object):
    def __init__(self, path):
        try:
            normalized_path = os.path.normpath(path)
            self._bucket_name, self._key = normalized_path.split('/', 1)
        except ValueError:
            raise ValueError('path should specify the bucket an object key/prefix')

    def bucket_name(self):
        return self._bucket_name

    def bucket(self):
        client = get_client()
        return client.get_bucket(self.bucket_name())

    def key(self):
        if self._key == '':
            raise ValueError('object key cannot be empty')
        return self._key

    def dir_key(self):
        if self._key == '':
            return self._key
        return self._key + '/'

    def put(self, data):
        bucket = self.bucket()
        blob = bucket.blob(self.key())
        blob.upload_from_string(data)

    def put_fileobj(self, file):
        bucket = self.bucket()
        blob = bucket.blob(self.key())
        blob.upload_from_file(file)

    def mkdir(self, **kwargs):
        bucket = self.bucket()
        blob = bucket.blob(self.dir_key())
        blob.upload_from_string('')

    # TODO: batch processing?
    def exists(self):
        return self.file_exists() or self.dir_exists()

    def file_exists(self):
        bucket = self.bucket()
        blob = bucket.blob(self.key())
        return blob.exists()

    def dir_exists(self):
        client = get_client()
        iterator = client.list_blobs(self.bucket(), prefix=self.dir_key(), max_results=1)
        return len(list(iterator)) > 0

    def dir_size(self):
        client = get_client()
        iterator = client.list_blobs(self.bucket(), prefix=self.dir_key())
        return sum([obj.size for obj in iterator])

    def open(self, mode='rb'):
        storage = GoogleCloudStorage(bucket_name=self.bucket_name())
        return storage.open(self.key(), mode=mode)

    def list_dir(self):
        client = get_client()
        iterator = client.list_blobs(self.bucket_name(), prefix=self.dir_key(), delimiter='/')
        blobs = list(iterator)
        prefixes = iterator.prefixes

        files = []
        dirs = []

        for blob in blobs:
            name = blob.name.replace(self.dir_key(), '', 1)
            if name != '':
                size = readable_size(blob.size)
                modified = blob.updated.strftime("%Y-%m-%d")
                files.append(FileInfo(name, size, modified))

        for prefix in prefixes:
            dirs.append(DirectoryInfo(prefix.replace(self.dir_key(), '', 1)[:-1]))

        files.sort()
        dirs.sort()

        return files, dirs

    def url(self):
        storage = GoogleCloudStorage(bucket_name=self.bucket_name())
        return storage.url(self.key())

    def delete(self):
        bucket = self.bucket()
        blob = bucket.blob(self.key())
        blob.delete()

    def delete_recursive(self):
        bucket = self.bucket()
        client = bucket.client

        try:
            bucket.blob(self.key()).delete()
        except NotFound:
            pass

        blobs = list(client.list_blobs(self.bucket(), prefix=self.dir_key()))
        bucket.delete_blobs(blobs=blobs)

    def cp(self, other):
        pass

    def cp_file(self, other):
        pass

    def cp_directory(self, other):
        pass


class OpenS3Object(object):
    def __init__(self, streaming_body):
        self._streaming_body = streaming_body

    def __enter__(self):
        return self._streaming_body

    def __exit__(self, _exc_type, _exc_val, _exc_tb):
        self._streaming_body.close()

    def read(self, *args):
        return self._streaming_body.read(*args)

def s3_signed_url(bucket_name, key):
    pass
    # return get_s3_resource().meta.client.generate_presigned_url('get_object', Params={'Bucket': bucket_name, 'Key': key}, ExpiresIn=3600)

def s3_directory_size(bucket_name, path):
    if not path.endswith('/'):
        path += '/'

    iterator = get_client().list_blobs(bucket_name, prefix=path)
    return sum(obj.size for obj in iterator)

def s3_upload_folder(bucket_name, path1, path2):
    """
    Upload files at path1 on the disk to path2 in the bucket.

    path1 should be an absolute path.
    """
    s3 = session.resource('s3')

    if path1.endswith('/') or path2.endswith('/'):
        raise ValueError('path1 and path2 must not end with "/"')

    for dirpath, subdirs, files in os.walk(path1):
        for f in files:
            src = os.path.join(dirpath, f)
            dst = os.path.join(dirpath.replace(path1, path2, 1), f)
            s3.meta.client.upload_file(src, bucket_name, dst)

def s3_mv_object(bucket_name, path1, path2):
    """
    Move object at path1 to path2 in a bucket.

    """
    pass
    # if path1.endswith('/') or path2.endswith('/'):
    #     raise ValueError('path1 and path2 must not end with "/"')

    # s3 = session.resource('s3')
    # print('mv:', path1, '->', path2)
    # # Copy object
    # s3.Object(bucket_name, path2).copy_from(
    #     CopySource={'Bucket': bucket_name, 'Key': path1})
    # # Delete original
    # s3.Object(bucket_name, path1).delete()

def s3_mv_folder(bucket_name, path1, path2):
    """
    Move all objects within 'folder' path1 to 'folder' path2.

    Aka, copy and delete all objects with prefix path1 to prefix path2.

    eg. s3_mv_folder('mybucket', 'a/b', 'A') applied to:
    - a/b/c/hello1.txt
    - a/b/hello2.txt

    Produces:
    - A/c/hello1.txt
    - A/hello2.txt

    """
    pass
    # if path1.endswith('/') or path2.endswith('/'):
    #     raise ValueError('path1 and path2 must not end with "/"')
    # # Ensure this is only moving items within 'folders'.
    # path1 += '/'
    # path2 += '/'

    # s3 = session.resource('s3')

    # bucket = s3.Bucket(bucket_name)

    # for obj in bucket.objects.filter(Prefix=path1):
    #     src_key = obj.key

    #     print('mv:', src_key, '->', src_key.replace(path1, path2, 1))
    #     s3.Object(bucket_name, src_key.replace(path1, path2, 1)).copy_from(
    #         CopySource={'Bucket': bucket_name, 'Key': src_key})
    #     obj.delete()

def s3_mv_items(bucket_name, path1, path2):
    # try:
    s3_mv_object(bucket_name, path1, path2)
    # except botocore.exceptions.ClientError as e:
    #     if e.response['Error']['Code'] != 'NoSuchKey':
    #         raise e
    s3_mv_folder(bucket_name, path1, path2)
