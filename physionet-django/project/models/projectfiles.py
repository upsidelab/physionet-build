
"""
Module containing project-related file logic.
"""
from abc import abstractmethod
import hashlib
import os

from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse

from physionet.abcmodel import AbstractModelMeta
from physionet.utility import sorted_tree_files, zip_dir
from project.utility import (list_items, get_dir_breadcrumbs, get_file_info,
    get_directory_info)
from project.utility import clear_directory
from project.validators import validate_relative_path


class ProjectFiles(models.Model, metaclass=AbstractModelMeta):
    """
    Abstract class inherited by ActiveProject and PublishedProject.
    Contains logic for dealing with project files.

    Note: Make sure this class is inherited after the ones below due to
    Python inheritance MRO.
    """
    class Meta:
        abstract = True

    def get_file_info(self, subdir):
        """
        Get the files, directories, and breadcrumb info for a project's
        subdirectory. Helper function for generating the files panel.

        If the subdirectory is invalid, return placeholder results instead
        of raising an exception.
        """
        display_files = display_dirs = dir_breadcrumbs = ()
        parent_dir = file_error = None

        # Sanitize subdir for illegal subdir path.
        try:
            self.validate_project_path(relative_path=subdir)
        except ValidationError:
            file_error = 'Invalid subdirectory'
            return display_files, display_dirs, dir_breadcrumbs, parent_dir, file_error

        try:
            display_files, display_dirs = self.get_directory_content(
                subdir=subdir)
        except FileNotFoundError:
            file_error = 'Directory not found'
        except OSError:
            file_error = 'Unable to read directory'

        # Return breadcrumbs back
        dir_breadcrumbs = get_dir_breadcrumbs(subdir)
        parent_dir = os.path.split(subdir)[0]

        return display_files, display_dirs, dir_breadcrumbs, parent_dir, file_error

    def get_directory_content(self, subdir=''):
        """
        Return information for displaying files and directories from
        the project's file root.
        """
        inspect_dir = os.path.join(self.file_root(), subdir)

        file_names, dir_names = list_items(inspect_dir)
        display_files, display_dirs = [], []

        # Files require desciptive info and download links
        for file in file_names:
            file_info = get_file_info(os.path.join(inspect_dir, file))
            file_info.url = self.file_display_url(subdir=subdir, file=file)
            file_info.raw_url = self.file_url(subdir=subdir, file=file)
            file_info.download_url = file_info.raw_url + '?download'
            display_files.append(file_info)

        # Directories require links
        for dir_name in dir_names:
            dir_info = get_directory_info(os.path.join(inspect_dir, dir_name))
            dir_info.full_subdir = os.path.join(subdir, dir_name)
            display_dirs.append(dir_info)

        return display_files, display_dirs

    def validate_project_path(self, relative_path):
        """
        Validate that the provided path contains a legal pattern
        that results in a valid subdirectory/subfile of the project
        """
        validate_relative_path(relative_path)
        # Extra check just in case
        if not os.path.join(self.file_root(), relative_path).startswith(self.file_root()):
            raise ValidationError('Invalid path')

    @abstractmethod
    def file_root(self):
        """
        Root directory containing the project's files
        """
        pass

    @abstractmethod
    def file_url(self, subdir, file):
        """
        Url of a file to download in this project
        """
        pass

    @abstractmethod
    def file_display_url(self, subdir, file):
        """
        URL of a file to display in this project
        """
        pass

    @abstractmethod
    def remove_files(self):
        """
        Remove files of this project
        """
        pass

class ActiveProjectFiles:
    """
    Class inherited by ActiveProject. Contains logic for dealing with project files.
    """
    def file_root(self):
        return os.path.join(self.__class__.FILE_ROOT, self.slug)

    def file_url(self, subdir, file):
        return reverse('serve_active_project_file',
            args=(self.slug, os.path.join(subdir, file)))

    def file_display_url(self, subdir, file):
        return reverse('display_active_project_file',
            args=(self.slug, os.path.join(subdir, file)))

    def remove_files(self):
        clear_directory(self.file_root())

class PublishedProjectFiles:
    """
    Class inherited by PublishedProject. Contains logic for dealing with project files.
    """
    def file_root(self):
        return os.path.join(self.project_file_root(), self.version)

    def file_url(self, subdir, file):
        full_file_name = os.path.join(subdir, file)
        return reverse('serve_published_project_file',
            args=(self.slug, self.version, full_file_name))

    def file_display_url(self, subdir, file):
        return reverse('display_published_project_file',
            args=(self.slug, self.version, os.path.join(subdir, file)))

    def remove_files(self):
        clear_directory(self.file_root())
        self.remove_zip()
        self.set_storage_info()

    def deprecate_files(self, delete_files):
        """
        Label the project's files as deprecated. Option of deleting
        files.
        """
        self.deprecated_files = True
        self.save()
        if delete_files:
            self.remove_files()

    def zip_name(self, full=False):
        """
        Name of the zip file. Either base name or full path name.
        """
        name = '{}.zip'.format(self.slugged_label())
        if full:
            name = os.path.join(self.project_file_root(), name)
        return name

    def make_zip(self):
        """
        Make a (new) zip file of the main files.
        """
        fname = self.zip_name(full=True)
        if os.path.isfile(fname):
            os.remove(fname)

        zip_dir(zip_name=fname, target_dir=self.file_root(),
            enclosing_folder=self.slugged_label())

        self.compressed_storage_size = os.path.getsize(fname)
        self.save()

    def remove_zip(self):
        fname = self.zip_name(full=True)
        if os.path.isfile(fname):
            os.remove(fname)
            self.compressed_storage_size = 0
            self.save()

    def zip_url(self):
        """
        The url to download the zip file from. Only needed for open
        projects
        """
        if self.access_policy:
            raise Exception('This should not be called by protected projects')
        else:
            return os.path.join('published-projects', self.slug, self.zip_name())

    def make_checksum_file(self):
        """
        Make the checksums file for the main files
        """
        fname = os.path.join(self.file_root(), 'SHA256SUMS.txt')
        if os.path.isfile(fname):
            os.remove(fname)

        with open(fname, 'w') as outfile:
            for f in sorted_tree_files(self.file_root()):
                if f != 'SHA256SUMS.txt':
                    h = hashlib.sha256()
                    with open(os.path.join(self.file_root(), f), 'rb') as fp:
                        block = fp.read(h.block_size)
                        while block:
                            h.update(block)
                            block = fp.read(h.block_size)
                    outfile.write('{} {}\n'.format(h.hexdigest(), f))

        self.set_storage_info()


class StorageRequest(BaseInvitation):
    """
    A request for storage capacity for a project
    """
    # Requested storage size in GB. Max = 10Tb
    request_allowance = models.SmallIntegerField(
        validators=[MaxValueValidator(10240), MinValueValidator(1)])
    responder = models.ForeignKey('user.User', null=True,
        on_delete=models.SET_NULL)
    response_message = models.CharField(max_length=10000, default='', blank=True)

    def __str__(self):
        return '{0}GB for project: {1}'.format(self.request_allowance,
                                               self.project.__str__())


class GCP(models.Model):
    """
    Store all of the Google Cloud information with a relation to a project.
    """
    project = models.OneToOneField('project.PublishedProject', related_name='gcp',
        on_delete=models.CASCADE)
    bucket_name = models.CharField(max_length=150, null=True)
    access_group = models.CharField(max_length=170, null=True)
    is_private = models.BooleanField(default=False)
    sent_zip = models.BooleanField(default=False)
    sent_files = models.BooleanField(default=False)
    managed_by = models.ForeignKey('user.User', related_name='gcp_manager',
        on_delete=models.CASCADE)
    creation_datetime = models.DateTimeField(auto_now_add=True)
    finished_datetime = models.DateTimeField(null=True)
