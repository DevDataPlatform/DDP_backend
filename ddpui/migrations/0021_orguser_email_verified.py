# Generated by Django 4.1.7 on 2023-07-03 07:04

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ddpui", "0020_orgprefectblock_command_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="orguser",
            name="email_verified",
            field=models.BooleanField(default=False),
        ),
    ]