
"""
Module containing project-related file logic.
"""
from abc import abstractmethod
import os

from django.core.exceptions import ValidationError
from django.urls import reverse

from physionet.abcmodel import ABCModel
from project.utility import (list_items, get_dir_breadcrumbs, get_file_info,
    get_directory_info)
from project.utility import clear_directory
from project.validators import validate_relative_path


class ProjectFiles(ABCModel):
    """
    Abstract class inherited by ActiveProject and PublishedProject.
    Contains logic for dealing with project files.

    Note: Make sure this class is inherited after the ones below due to
    Python inheritance MRO.
    """

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
