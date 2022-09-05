# Generated by Django 2.2 on 2022-03-23 15:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iaas', '0028_model_ordering'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='project',
            name='project_send_bill_id',
        ),
        migrations.RenameField(
            model_name='project',
            old_name='send_bill_id',
            new_name='reseller_id',
        ),
        migrations.AddIndex(
            model_name='project',
            index=models.Index(fields=['reseller_id'], name='project_reseller_id'),
        ),
    ]