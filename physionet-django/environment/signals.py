from django.dispatch import receiver
from django.apps import apps
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models.signals import post_init, post_save

from environment.tasks import stop_environments_with_expired_access
from environment.utilities import user_has_billing_setup


User = get_user_model()

Training = apps.get_model("user", "Training")

DataAccessRequest = apps.get_model("project", "DataAccessRequest")


@receiver(post_init, sender=User)
def memoize_original_credentialing_status(instance: User, **kwargs):
    instance._original_is_credentialed = instance.is_credentialed


@receiver(post_save, sender=User)
def schedule_stop_environments_if_credentialing_revoked(instance: User, **kwargs):
    if not user_has_billing_setup(instance):
        return

    if not instance.is_credentialed and instance._original_is_credentialed:
        stop_environments_with_expired_access(instance.id)


@receiver(post_init, sender=Training)
def memoize_original_validity(instance: Training, **kwargs):
    instance._original_is_valid = instance.is_valid()


@receiver(post_save, sender=Training)
def schedule_stop_environment_if_training_accepted(instance: Training, **kwargs):
    user = instance.user
    if not user_has_billing_setup(user):
        return

    if instance.is_valid() and not instance._original_is_valid:
        schedule = instance.process_datetime + instance.training_type.valid_duration
        stop_environments_with_expired_access(user.id, schedule=schedule)


@receiver(post_init, sender=DataAccessRequest)
def memoize_original_acceptation_status(instance: DataAccessRequest, **kwargs):
    instance._original_is_accepted = instance.is_accepted()
    instance._original_is_revoked = instance.is_revoked()


@receiver(post_save, sender=DataAccessRequest)
def schedule_stop_environment_if_data_access_request_accepted_or_revoked(
    instance: DataAccessRequest, **kwargs
):
    user = instance.requester
    if not user_has_billing_setup(user):
        return

    request_was_accepted = instance.is_accepted() and not instance._original_is_accepted
    access_was_revoked = instance.is_revoked() and not instance._original_is_revoked
    if request_was_accepted:
        if request_was_accepted and not instance.duration:  # Indefinite access
            return
        schedule = timezone.now() + instance.duration
        stop_environments_with_expired_access(user.id, schedule=schedule)
    elif access_was_revoked:
        stop_environments_with_expired_access(user.id)
