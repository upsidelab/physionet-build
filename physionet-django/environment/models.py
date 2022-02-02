from django.db import models
from django.core.validators import EmailValidator


class CloudIdentity(models.Model):
    user = models.OneToOneField('user.User', related_name='cloud_identity', on_delete=models.CASCADE)
    userid = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=255, unique=True, validators=[EmailValidator()])
