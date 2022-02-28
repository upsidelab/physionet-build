from django.dispatch import receiver
from django.apps import apps
from django.contrib.auth import get_user_model
from django.db.models.signals import post_init, post_save

from environment.tasks import stop_environments_with_expired_access


User = get_user_model()

Training = apps.get_model("project", "Training")


@receiver(post_init, sender=User)
def memoize_original_credentialing_status(instance: User, **kwargs):
    instance._original_is_credentialed = instance.is_credentialed


@receiver(post_save, sender=User)
def schedule_stop_environments_if_credentialing_revoked(instance: User, **kwargs):
    if not instance.is_credentialed and instance._original_is_credentialed:
        stop_environments_with_expired_access(instance.id)


@receiver(post_init, sender=Training)
def memoize_original_validity(instance: Training, **kwargs):
    instance._original_validity = instance.is_valid()


@receiver(post_init, sender=Training)
def schedule_environment_(instance: Training, **kwargs):
    if instance.is_valid() and not instance._original_validity:
        schedule = instance.process_datetime + instance.training_type.valid_duration
        stop_environments_with_expired_access(instance.id, schedule=schedule)
