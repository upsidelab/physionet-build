from django.db import models
from django.core.validators import EmailValidator, RegexValidator


class CloudIdentity(models.Model):
    user = models.OneToOneField('user.User', related_name='cloud_identity', on_delete=models.CASCADE)
    userid = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=255, unique=True, validators=[EmailValidator()])


class BillingSetup(models.Model):
    cloud_identity = models.ForeignKey(CloudIdentity, on_delete=models.CASCADE)
    billing_account_id = models.CharField(
        max_length=20,
        unique=True,
        validators=[RegexValidator('\A[A-Z0-9]{6}-[A-Z0-9]{6}-[A-Z0-9]{6}\z')]
    )
    # TODO: status?