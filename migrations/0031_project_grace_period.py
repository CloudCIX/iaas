# Generated by Django 2.2 on 2022-09-16 12:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iaas', '0030_remove_member_id_from_record'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='grace_period',
            field=models.IntegerField(default=168, null=True),
        ),
        migrations.AddIndex(
            model_name='project',
            index=models.Index(fields=['grace_period'], name='project_grace_period'),
        ),
    ]
