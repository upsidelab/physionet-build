# Generated by Django 4.1.9 on 2023-07-05 16:56

from django.db import migrations


class Migration(migrations.Migration):
    MIGRATE_AFTER_INSTALL = True

    dependencies = [
        ('user', '0055_auto_20230330_1723'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='credentialreview',
            name='appears_correct',
        ),
        migrations.RemoveField(
            model_name='credentialreview',
            name='course_name_provided',
        ),
        migrations.RemoveField(
            model_name='credentialreview',
            name='fields_complete',
        ),
        migrations.RemoveField(
            model_name='credentialreview',
            name='lang_understandable',
        ),
        migrations.RemoveField(
            model_name='credentialreview',
            name='ref_appropriate',
        ),
        migrations.RemoveField(
            model_name='credentialreview',
            name='ref_approves',
        ),
        migrations.RemoveField(
            model_name='credentialreview',
            name='ref_course_list',
        ),
        migrations.RemoveField(
            model_name='credentialreview',
            name='ref_has_papers',
        ),
        migrations.RemoveField(
            model_name='credentialreview',
            name='ref_is_supervisor',
        ),
        migrations.RemoveField(
            model_name='credentialreview',
            name='ref_knows_applicant',
        ),
        migrations.RemoveField(
            model_name='credentialreview',
            name='ref_searchable',
        ),
        migrations.RemoveField(
            model_name='credentialreview',
            name='ref_understands_privacy',
        ),
        migrations.RemoveField(
            model_name='credentialreview',
            name='research_summary_clear',
        ),
        migrations.RemoveField(
            model_name='credentialreview',
            name='user_details_consistent',
        ),
        migrations.RemoveField(
            model_name='credentialreview',
            name='user_has_papers',
        ),
        migrations.RemoveField(
            model_name='credentialreview',
            name='user_org_known',
        ),
        migrations.RemoveField(
            model_name='credentialreview',
            name='user_searchable',
        ),
        migrations.RemoveField(
            model_name='credentialreview',
            name='user_understands_privacy',
        ),
    ]
