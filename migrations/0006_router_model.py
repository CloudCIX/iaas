# Generated by Django 2.2.14 on 2020-10-20 11:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iaas', '0005_router_interfaces'),
    ]

    operations = [
        migrations.AddField(
            model_name='router',
            name='model',
            field=models.CharField(default='', max_length=64),
        ),
    ]