# Generated by Django 2.2.27 on 2022-03-22 11:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0036_training_2"),
    ]

    operations = [
        migrations.AlterField(
            model_name="training",
            name="reviewer",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="reviewed_trainings",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="training",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="trainings",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
