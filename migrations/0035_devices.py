# Generated by Django 2.2 on 2023-02-16 10:00

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('iaas', '0034_firewallrule_comma_ports'),
    ]

    operations = [
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.DateTimeField(null=True)),
                ('extra', django.contrib.postgres.fields.jsonb.JSONField(default=dict)),
                ('id_on_host', models.CharField(max_length=12)),
            ],
            options={
                'db_table': 'device',
                'ordering': ['id_on_host'],
            },
        ),
        migrations.CreateModel(
            name='DeviceType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.DateTimeField(null=True)),
                ('extra', django.contrib.postgres.fields.jsonb.JSONField(default=dict)),
                ('description', models.TextField()),
                ('sku', models.CharField(max_length=250)),
            ],
            options={
                'db_table': 'device_type',
                'ordering': ['id'],
            },
        ),
        migrations.AddField(
            model_name='vm',
            name='gpu',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='vmhistory',
            name='gpu_quantity',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='vmhistory',
            name='gpu_sku',
            field=models.CharField(max_length=250, null=True),
        ),
        migrations.AddIndex(
            model_name='vmhistory',
            index=models.Index(fields=['gpu_sku'], name='vm_history_gpu_sku'),
        ),
        migrations.AddIndex(
            model_name='devicetype',
            index=models.Index(fields=['id'], name='device_type_id'),
        ),
        migrations.AddField(
            model_name='device',
            name='device_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='iaas.DeviceType'),
        ),
        migrations.AddField(
            model_name='device',
            name='server',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='iaas.Server'),
        ),
        migrations.AddField(
            model_name='device',
            name='vm',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='iaas.VM'),
        ),
        migrations.AddIndex(
            model_name='device',
            index=models.Index(fields=['id'], name='device_id'),
        ),
    ]