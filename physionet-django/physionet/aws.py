import boto3
from django.conf import settings

# One session per main django process.
# One resource per thread. https://boto3.amazonaws.com/v1/documentation/api/latest/guide/resources.html?highlight=multithreading#multithreading-or-multiprocessing-with-resources
session = boto3.Session(
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
)


def s3_mv_object(bucket_name, path1, path2):
    """
    Move object at path1 to path2 in a bucket.

    """
    if path1.endswith('/') or path2.endswith('/'):
        raise ValueError('path1 and path2 must not end with "/"')

    s3 = session.resource('s3')
    # Copy object
    s3.Object(bucket_name, path2).copy_from(
        CopySource={'Bucket':bucket_name, 'Key':path1})
    # Delete original
    s3.Object(bucket_name, path1).delete()

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
    if path1.endswith('/') or path2.endswith('/'):
        raise ValueError('path1 and path2 must not end with "/"')
    # Ensure this is only moving items within 'folders'.
    path1 += '/'
    path2 += '/'

    s3 = session.resource('s3')
    bucket = s3.Bucket(bucket_name)

    for obj_summary in bucket.objects.filter(Prefix=path1):
        src_key = obj_summary.key
        if src_key.endswith('/'):
            continue

        s3.Object(bucket_name, src_key.replace(path1, path2, 1)).copy_from(
            CopySource={ 'Bucket':bucket_name, 'Key': src_key })
        obj_summary.delete()


def s3_ls(bucket_name, folder_path):
    """
    Like running 'ls' on an S3 'folder'.

    Note that returned folder_names may differ from what is observed
    in the AWS console, since only 'folders' that are explicitly
    created will show up here. ie. Implicit folders from creating
    an object with key dir1/dir2/filename.txt will not show up.

    """
    if folder_path.endswith('/'):
        raise ValueError('folder_path must not end with "/"')

    if folder_path != '':
        # Ensure this is only checking items within a 'folder'.
        folder_path += '/'
    slash_count = folder_path.count('/')

    s3 = session.resource('s3')
    bucket = s3.Bucket(bucket_name)

    object_names, folder_names = [], []
    for obj_summary in bucket.objects.filter(Prefix=folder_path):
        item_key = obj_summary.key

        if item_key == folder_path:
            continue
        if item_key.endswith('/') and item_key.count('/') == slash_count + 1:
            folder_names.append(item_key)
        elif item_key.count('/') == slash_count:
            object_names.append(item_key)

    return object_names, folder_names


def s3_create_folder(bucket_name, folder_name, subdir):
    """
    Create a 'folder' in an S3 bucket from a subdir.
    """
    # Sanitize


    s3 = session.resource('s3')
    bucket = s3.Bucket(bucket_name)
    bucket.put_object(key=f'{subdir}/{folder_name}/')  # trailing slash very important


