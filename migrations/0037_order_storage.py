# Generated by Django 2.2 on 2023-04-28 11:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('iaas', '0036_server_devices'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='storage',
            options={'ordering': ['-primary', 'name']},
        ),
    ]
