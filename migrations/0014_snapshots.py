# Generated by Django 2.2 on 2021-08-09 15:09

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('iaas', '0013_create_bom_model'),
    ]

    operations = [
        migrations.CreateModel(
            name='Snapshot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.DateTimeField(null=True)),
                ('extra', django.contrib.postgres.fields.jsonb.JSONField(default=dict)),
                ('active', models.BooleanField()),
                ('name', models.CharField(max_length=128)),
                ('state', models.IntegerField()),
                ('parent', models.ForeignKey(
                    null=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    to='iaas.Snapshot',
                )),
                ('vm', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='iaas.VM')),
            ],
            options={
                'db_table': 'snapshot',
            },
        ),
        migrations.AddIndex(
            model_name='snapshot',
            index=models.Index(fields=['id'], name='snapshot_id'),
        ),
        migrations.AddIndex(
            model_name='snapshot',
            index=models.Index(fields=['active'], name='snapshot_active'),
        ),
        migrations.AddIndex(
            model_name='snapshot',
            index=models.Index(fields=['name'], name='snapshot_name'),
        ),
        migrations.AddIndex(
            model_name='snapshot',
            index=models.Index(fields=['state'], name='snapshot_state'),
        ),
    ]
