# Generated by Django 4.1.7 on 2023-05-10 05:39

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ddpui", "0012_alter_org_dbt"),
    ]

    operations = [
        migrations.AddField(
            model_name="orgwarehouse",
            name="airbyte_destination_id",
            field=models.TextField(max_length=36, null=True),
        ),
    ]
