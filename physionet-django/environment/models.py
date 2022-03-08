from django.db import models
from django.core.validators import EmailValidator

from environment.validators import gcp_billing_account_id_validator


class CloudIdentity(models.Model):
    user = models.OneToOneField(
        "user.User", related_name="cloud_identity", on_delete=models.CASCADE
    )
    gcp_user_id = models.CharField(max_length=50, unique=True)
    email = models.EmailField(
        max_length=255, unique=True, validators=[EmailValidator()]
    )
    is_workspace_done = models.BooleanField(default=False)


class BillingSetup(models.Model):
    cloud_identity = models.OneToOneField(
        CloudIdentity, related_name="billing_setup", on_delete=models.CASCADE
    )
    billing_account_id = models.CharField(
        max_length=20, unique=True, validators=[gcp_billing_account_id_validator]
    )
