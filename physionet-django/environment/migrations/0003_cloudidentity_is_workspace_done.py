# Generated by Django 2.2.26 on 2022-03-07 15:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('environment', '0002_billingsetup'),
    ]

    operations = [
        migrations.AddField(
            model_name='cloudidentity',
            name='is_workspace_done',
            field=models.BooleanField(default=False),
        ),
    ]
