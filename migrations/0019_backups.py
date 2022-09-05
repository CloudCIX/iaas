# Generated by Django 2.2 on 2021-10-02 10:01

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('iaas', '0018_vm_snapshots'),
    ]

    operations = [
        migrations.CreateModel(
            name='Backup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.DateTimeField(null=True)),
                ('extra', django.contrib.postgres.fields.jsonb.JSONField(default=dict)),
                ('repository', models.IntegerField()),
                ('state', models.IntegerField()),
                ('time_valid', models.DateTimeField(auto_now_add=True, null=True)),
                ('vm', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='backups',
                    to='iaas.VM',
                )),
            ],
            options={
                'db_table': 'backup',
            },
        ),
        migrations.AddIndex(
            model_name='backup',
            index=models.Index(fields=['id'], name='backup_id'),
        ),
        migrations.AddIndex(
            model_name='backup',
            index=models.Index(fields=['repository'], name='backup_repository'),
        ),
        migrations.AddIndex(
            model_name='backup',
            index=models.Index(fields=['state'], name='backup_state'),
        ),
        migrations.AddIndex(
            model_name='backup',
            index=models.Index(fields=['time_valid'], name='backup_time_valid'),
        ),
    ]
