# Generated by Django 2.2 on 2022-01-10 14:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iaas', '0023_vm_userdata'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='public',
            field=models.BooleanField(default=True),
        ),
    ]