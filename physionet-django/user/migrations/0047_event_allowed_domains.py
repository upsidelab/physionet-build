# Generated by Django 3.1.14 on 2022-09-28 14:42

from django.db import migrations, models
import user.validators


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0046_event_eventparticipant'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='allowed_domains',
            field=models.CharField(blank=True, max_length=100, null=True,
                                   validators=[user.validators.validate_domain_list]),
        ),
    ]
