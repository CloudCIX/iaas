# Generated by Django 2.2 on 2022-01-20 15:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iaas', '0024_public_images'),
    ]

    operations = [
        migrations.AlterField(
            model_name='backup',
            name='time_valid',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
