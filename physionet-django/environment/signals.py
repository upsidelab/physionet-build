from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.db.models.signals import post_init, post_save

from environment.tasks import stop_environments_with_expired_access


User = get_user_model()


@receiver(post_init, sender=User)
def memoize_original_credentialing_status(instance: User, **kwargs):
    instance._original_is_credentialed = instance.is_credentialed


@receiver(post_save, sender=User)
def schedule_environment_cleanup_background_tasks(instance: User, **kwargs):
    if not instance.is_credentialed and instance._original_is_credentialed:
        stop_environments_with_expired_access(instance.id)
