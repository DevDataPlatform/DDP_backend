# Generated by Django 4.1.7 on 2023-03-31 10:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("ddpui", "0005_clientprefectblock"),
    ]

    operations = [
        migrations.AlterField(
            model_name="org",
            name="dbt",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="ddpui.orgdbt",
            ),
        ),
    ]
