from datetime import datetime, timedelta
from html import unescape
import os
import shutil
import uuid
import pytz
import logging
from distutils.version import StrictVersion

import bleach
import ckeditor.fields
from html2text import html2text
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.hashers import check_password, make_password
from django.db import models, transaction
from django.forms.utils import ErrorList
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html, strip_tags
from django.utils.text import slugify
from background_task import background
from django.utils.crypto import get_random_string

from project.modelfiles import ProjectFiles, ActiveProjectFiles, PublishedProjectFiles
from project.quota import DemoQuotaManager
from project.utility import get_tree_size, StorageInfo, LinkFilter
from project.validators import (validate_version, validate_slug,
                                MAX_PROJECT_SLUG_LENGTH,
                                validate_title, validate_topic)
from user.validators import validate_affiliation


LOGGER = logging.getLogger(__name__)
