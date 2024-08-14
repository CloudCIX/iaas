# Generated by Django 2.2 on 2022-09-21 11:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('iaas', '0031_project_grace_period'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='firewallrule',
            options={'ordering': ['order']},
        ),
        migrations.AlterModelOptions(
            name='route',
            options={'ordering': ['remote_subnet']},
        ),
        migrations.AlterModelOptions(
            name='servertype',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='snapshot',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='storage',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='storagetype',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='subnet',
            options={'ordering': ['address_range']},
        ),
        migrations.AlterModelOptions(
            name='vm',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='vpn',
            options={'ordering': ['description']},
        ),
        migrations.AlterModelOptions(
            name='vpnclient',
            options={'ordering': ['username']},
        ),
    ]