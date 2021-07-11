import os

from django.core.exceptions import ValidationError
from django.db import models

from project.utility import (list_items, get_dir_breadcrumbs, get_file_info,
    get_directory_info)
from project.validators import validate_subdir


class ProjectWithFiles(models.Model):
    """
    Abstract model to be inherited by all three project types.

    Contains logic for dealing with project files.
    """

    class Meta:
        abstract = True

    def get_file_info(self, subdir):
        """
        Get the files, directories, and breadcrumb info for a project's
        subdirectory.
        Helper function for generating the files panel
        """
        display_files = display_dirs = ()
        try:
            display_files, display_dirs = self.get_directory_content(
                subdir=subdir)
            file_error = None
        except (FileNotFoundError, ValidationError):
            file_error = 'Directory not found'
        except OSError:
            file_error = 'Unable to read directory'

        # Breadcrumbs
        dir_breadcrumbs = get_dir_breadcrumbs(subdir)
        parent_dir = os.path.split(subdir)[0]

        return display_files, display_dirs, dir_breadcrumbs, parent_dir, file_error

    def get_directory_content(self, subdir=''):
        """
        Return information for displaying files and directories from
        the project's file root.
        """
        # Get folder to inspect if valid
        inspect_dir = self.get_inspect_dir(subdir)
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

    def get_inspect_dir(self, subdir):
        """
        Return the folder to inspect if valid. subdir joined onto
        the file root of this project.
        """
        # Sanitize subdir for illegal characters
        validate_subdir(subdir)
        # Folder must be a subfolder of the file root
        # (but not necessarily exist or be a directory)
        inspect_dir = os.path.join(self.file_root(), subdir)
        if inspect_dir.startswith(self.file_root()):
            return inspect_dir
        else:
            raise Exception('Invalid directory request')
