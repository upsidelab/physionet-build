

class PublishedProject(Metadata, SubmissionInfo, PublishedProjectFiles, ProjectFiles):
    """
    A published project. Immutable snapshot.

    """
    # File storage sizes in bytes
    main_storage_size = models.BigIntegerField(default=0)
    compressed_storage_size = models.BigIntegerField(default=0)
    incremental_storage_size = models.BigIntegerField(default=0)
    publish_datetime = models.DateTimeField(auto_now_add=True)
    has_other_versions = models.BooleanField(default=False)
    deprecated_files = models.BooleanField(default=False)
    # doi = models.CharField(max_length=50, unique=True, validators=[validate_doi])
    # Temporary workaround
    doi = models.CharField(max_length=50, blank=True, null=True)
    slug = models.SlugField(max_length=MAX_PROJECT_SLUG_LENGTH, db_index=True,
        validators=[validate_slug])
    # Fields for legacy pb databases
    is_legacy = models.BooleanField(default=False)
    full_description = SafeHTMLField(default='')

    is_latest_version = models.BooleanField(default=True)
    # Featured content
    featured = models.PositiveSmallIntegerField(null=True)
    has_wfdb = models.BooleanField(default=False)
    display_publications = models.BooleanField(default=True)
    # Where all the published project files are kept, depending on access.
    PROTECTED_FILE_ROOT = os.path.join(settings.MEDIA_ROOT, 'published-projects')
    # Workaround for development
    if 'development' in os.environ['DJANGO_SETTINGS_MODULE']:
        PUBLIC_FILE_ROOT = os.path.join(settings.STATICFILES_DIRS[0], 'published-projects')
    else:
        PUBLIC_FILE_ROOT = os.path.join(settings.STATIC_ROOT, 'published-projects')

    SPECIAL_FILES = {
        'FILES.txt':'List of all files',
        'LICENSE.txt':'License for using files',
        'SHA256SUMS.txt':'Checksums of all files',
        'RECORDS.txt':'List of WFDB format records',
        'ANNOTATORS.tsv':'List of WFDB annotation file types'
    }

    class Meta:
        unique_together = (('core_project', 'version'),('featured',),)

    def __str__(self):
        return ('{0} v{1}'.format(self.title, self.version))

    def project_file_root(self):
        """
        Root directory containing the published project's files.

        This is the parent directory of the main and special file
        directories.
        """
        if self.access_policy:
            return os.path.join(PublishedProject.PROTECTED_FILE_ROOT, self.slug)
        else:
            return os.path.join(PublishedProject.PUBLIC_FILE_ROOT, self.slug)

    def storage_used(self):
        """
        Bytes of storage used by main files and compressed file if any
        """
        main = get_tree_size(self.file_root())
        compressed = os.path.getsize(self.zip_name(full=True)) if os.path.isfile(self.zip_name(full=True)) else 0
        return main, compressed

    def set_storage_info(self):
        """
        Sum up the file sizes of the project and set the storage info
        fields
        """
        self.main_storage_size, self.compressed_storage_size = self.storage_used()
        self.save()

    def slugged_label(self):
        """
        Slugged readable label from the title and version. Used for
        the project's zipped files
        """
        return '-'.join((slugify(self.title), self.version.replace(' ', '-')))

    def has_access(self, user):
        """
        Whether the user has access to this project's files
        """
        if self.deprecated_files:
            return False

        if self.access_policy == 2 and (
            not user.is_authenticated or not user.is_credentialed):
            return False
        elif self.access_policy == 1 and not user.is_authenticated:
            return False

        if self.is_self_managed_access:
            return DataAccessRequest.objects.filter(
                project=self, requester=user,
                status=DataAccessRequest.ACCEPT_REQUEST_VALUE).exists()
        elif self.access_policy:
            return DUASignature.objects.filter(
                project=self, user=user).exists()

        return True

    def can_approve_requests(self, user):
        """
        Whether the user can view and respond to access requests to self managed
        projects
        """
        # check whether user is the corresponding author of the project
        is_corresponding = user == self.corresponding_author().user
        return is_corresponding or self.is_data_access_reviewer(user)

    def is_data_access_reviewer(self, user):
        return DataAccessRequestReviewer.objects.filter(
            reviewer=user, is_revoked=False, project=self).exists()

    def get_storage_info(self, force_calculate=True):
        """
        Return an object containing information about the project's
        storage usage. Main, compressed, total files, and allowance.

        This function always returns the cached information stored in
        the model.  The force_calculate argument has no effect.
        """
        main = self.main_storage_size
        compressed = self.compressed_storage_size
        return StorageInfo(allowance=self.core_project.storage_allowance,
            used=main+compressed, include_remaining=False, main_used=main,
            compressed_used=compressed)

    def remove(self, force=False):
        """
        Remove the project and its files. Probably will never be used
        in production. `force` argument is for safety.

        """
        if force:
            shutil.rmtree(self.file_root())
            return self.delete()
        else:
            raise Exception('Make sure you want to remove this item.')

    def submitting_user(self):
        "User who is the submitting author"
        return self.authors.get(is_submitting=True).user

    def can_publish_new(self, user):
        """
        Whether the user can publish a new version of this project
        """
        if user == self.submitting_user() and not self.core_project.active_new_version():
            return True

        return False

    def can_manage_data_access_reviewers(self, user):
        return user == self.corresponding_author().user

    def add_topic(self, topic_description):
        """
        Tag this project with a topic
        """

        published_topic = PublishedTopic.objects.filter(
            description=topic_description.lower())
        # Create the published topic object first if it doesn't exist
        if published_topic.count():
            published_topic = published_topic.get()
        else:
            published_topic = PublishedTopic.objects.create(
                description=topic_description.lower())

        published_topic.projects.add(self)
        published_topic.project_count += 1
        published_topic.save()

    def remove_topic(self, topic_description):
        """
        Remove the topic tag from this project
        """
        published_topic = PublishedTopic.objects.filter(
            description=topic_description.lower())

        if published_topic.count():
            published_topic = published_topic.get()
            published_topic.projects.remove(self)
            published_topic.project_count -= 1
            published_topic.save()

            if published_topic.project_count == 0:
                published_topic.delete()

    def set_topics(self, topic_descriptions):
        """
        Set the topic tags for this project.

        topic_descriptions : list of description strings
        """
        existing_descriptions = [t.description for t in self.topics.all()]

        # Add these topics
        for td in set(topic_descriptions) - set(existing_descriptions):
            self.add_topic(td)

        # Remove these topics
        for td in set(existing_descriptions) - set(topic_descriptions):
            self.remove_topic(td)

    def set_version_order(self):
        """
        Order the versions by number.
        Then it set a correct version order and a correct latest version
        """
        published_projects = self.core_project.get_published_versions()
        project_versions = []
        for project in published_projects:
            project_versions.append(project.version)
        sorted_versions = sorted(project_versions, key=StrictVersion)

        for indx, version in enumerate(sorted_versions):
            tmp = published_projects.get(version=version)
            tmp.version_order = indx
            tmp.has_other_versions = True
            tmp.is_latest_version = False
            if sorted_versions[-1] == version:
                tmp.is_latest_version = True
            tmp.save()




@background()
def move_files_as_readonly(pid, dir_from, dir_to, make_zip):
    """
    Schedule a background task to set the files as read only.
    If a file starts with a Shebang, then it will be set as executable.
    """

    published_project = PublishedProject.objects.get(id=pid)

    published_project.make_checksum_file()

    quota = published_project.quota_manager()
    published_project.incremental_storage_size = quota.bytes_used
    published_project.save(update_fields=['incremental_storage_size'])

    published_project.set_storage_info()

    # Make the files read only
    file_root = published_project.project_file_root()
    for root, dirs, files in os.walk(file_root):
        for f in files:
            fline = open(os.path.join(root, f), 'rb').read(2)
            if fline[:2] == b'#!':
                os.chmod(os.path.join(root, f), 0o555)
            else:
                os.chmod(os.path.join(root, f), 0o444)

        for d in dirs:
            os.chmod(os.path.join(root, d), 0o555)

    if make_zip:
        published_project.make_zip()
