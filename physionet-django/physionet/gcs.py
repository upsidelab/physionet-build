import os

from django.conf import settings
from django.core.files.storage import get_storage_class
from storages.backends.gcloud import GoogleCloudStorage

from physionet.settings.base import StorageTypes


class GCSObjectException(Exception):
    pass


class GCSObject:
    """
    The representation of an object in Google Cloud Storage.
    This class defines a set of useful operations which can be applied to the GCS object.

    Path has to be passed to the constructor in the following format:
    path="{bucket_name}/{object_name}"
    Paths ending in '/' point to a directory.

    Example 1:
        gcs_file = GCSObject(path="physionet/europe/cannes.jpg")
            bucket = physionet
            object = europe/cannes.jpg

    Example 2:
        gcs_dir = GCSObject(path="physionet/projectfiles/")
            bucket = physionet
            object = projectfiles/
    """
    def __init__(self, path, storage_klass=None):
        if settings.STORAGE_TYPE != StorageTypes.GCP and storage_klass is None:
            raise GCSObjectException(
                f"The default `STORAGE_TYPE` is not set to GCP. You can pass custom `storage_klass`."
                f"{self.__class__.__name__} works only with Storage class that can manage files stored in GCS."
            )
        self._storage, self._object_name = self._retrieve_data_from_path(path, storage_klass)

    def __repr__(self):
        return f'{self.__class__.__name__}(Bucket={self.bucket.name}, Object="{self.name}")'

    @property
    def bucket(self):
        return self._storage.bucket

    @property
    def blob(self):
        return self._storage.bucket.blob(self.name)

    @property
    def url(self):
        return self._storage.url(self.name)

    @property
    def client(self):
        return self._storage.client

    @property
    def name(self):
        return self._object_name

    def open(self, mode):
        return self._storage.open(self.name, mode=mode)

    def upload_from_string(self, content):
        self.blob.upload_from_string(content)

    def upload_from_file(self, file):
        self.blob.upload_from_file(file)

    def exists(self):
        return True if self.bucket.get_blob(self.name) else False

    def mkdir(self):
        """An empty object in GCS is a zero-byte object with a name ending in `/`."""
        if not self.is_dir():
            raise GCSObjectException(f'The {repr(self)} is not a directory.')

        if self.exists():
            raise GCSObjectException(f'The name `{self.name}` is already taken.')

        self.blob.upload_from_string('')

    def size(self):
        """Size of the object/all objects in the dictionary, in bytes. """
        if self.is_dir():
            return sum(obj.size for obj in self.bucket.list_blobs(prefix=self.name))

        file = self.bucket.get_blob(self.blob.name)
        if not file:
            raise GCSObjectException('The specified file does not exist')
        return file.size

    def ls(self, delimiter=None):
        """List directory contents. Returns an iterator of blobs."""
        if not self.is_dir():
            raise GCSObjectException(f'The {repr(self)} is not a directory.')

        return self.bucket.list_blobs(prefix=self.name, delimiter=delimiter)

    def rm(self):
        if self.is_dir():
            self.bucket.delete_blobs(list(self.ls()))
        else:
            self.bucket.delete_blob(self.name)

    def cp(self, gcs_obj, ignored_files=None):
        if not gcs_obj.is_dir():
            raise GCSObjectException('The target path must point on directory.')

        if not self.is_dir() and ignored_files:
            raise GCSObjectException('`ignored_files` does not work when copying a file.')

        if self.is_dir():
            self._cp_dir(gcs_obj, ignored_files)
        else:
            self._cp_file(gcs_obj)

    def mv(self, gcs_obj, ignored_files=None):
        if not gcs_obj.is_dir():
            raise GCSObjectException(
                'The target path must point on directory. If you want to rename a file use `.rename()` method.'
            )

        if self.is_dir():
            self._cp_dir(gcs_obj, ignored_files=ignored_files)
        else:
            self._cp_file(gcs_obj)

        self.rm()

    def rename(self, gcs_obj):
        if self.is_dir():
            self._cp_dir(gcs_obj, ignored_files=None)
        else:
            self._cp_file(gcs_obj)
        self.rm()

    def _cp_file(self, gcs_obj):
        self.bucket.copy_blob(self.blob, gcs_obj.bucket, new_name=self.blob.name.replace(self.name, gcs_obj.name, 1))

    def _cp_dir(self, gcs_obj, ignored_files):
        if ignored_files is None:
            ignored_files = []
        else:
            ignored_files = [os.path.join(self.name, f) for f in ignored_files]

        try:
            for blob in self.ls(delimiter='/'):
                if blob.name in ignored_files:
                    continue
                self.bucket.copy_blob(
                    blob,
                    gcs_obj.bucket,
                    new_name=blob.name.replace(self.name, gcs_obj.name, 1),
                )
        except ValueError:
            pass

    def is_dir(self):
        """Check if the object is a directory"""
        return True if self.name[-1] == '/' else False

    def _retrieve_data_from_path(self, path, storage_klass):
        """
        path="test-bucket/" -> test-bucket, "/"
        path="test-bucket/dir/image.jpg" -> test-bucket, "dir/image.jpg"
        path="test-bucket" -> raise GCSObjectException
        """
        if storage_klass is None:
            storage_klass = settings.DEFAULT_FILE_STORAGE

        add_slash = True if path[-1] == '/' else False
        path = os.path.normpath(path).split('/', 1)
        try:
            bucket_name, object_name = path
        except ValueError:
            bucket_name = path[0]
            if not add_slash:
                raise GCSObjectException('The provided path does not indicate a resource in the bucket.')
            object_name = '/'
        else:
            if add_slash:
                object_name += '/'

        return get_storage_class(storage_klass)(bucket_name=bucket_name), object_name


def create_bucket(name):
    client = GoogleCloudStorage().client
    bucket = client.bucket(name)
    bucket.location = settings.GCP_BUCKET_LOCATION
    bucket.iam_configuration.uniform_bucket_level_access_enabled = True
    client.create_bucket(bucket)
