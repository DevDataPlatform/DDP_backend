# Generated by Django 4.1.7 on 2023-04-15 05:49

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ddpui", "0004_invitation_invited_role"),
    ]

    operations = [
        migrations.AddField(
            model_name="orgprefectblock",
            name="displayname",
            field=models.CharField(max_length=100, null=True),
        ),
    ]
