# Generated by Django 2.2.26 on 2022-03-09 08:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('environment', '0003_cloudidentity_is_workspace_done'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cloudidentity',
            old_name='is_workspace_done',
            new_name='initial_workspace_setup_done',
        ),
    ]
