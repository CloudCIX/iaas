# Generated by Django 2.2 on 2022-02-17 10:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('iaas', '0027_projet_send_bill'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='allocation',
            options={'ordering': ['address_range']},
        ),
        migrations.AlterModelOptions(
            name='asn',
            options={'ordering': ['member_id']},
        ),
        migrations.AlterModelOptions(
            name='backup',
            options={'ordering': ['time_valid']},
        ),
        migrations.AlterModelOptions(
            name='cixblacklist',
            options={'ordering': ['cidr']},
        ),
        migrations.AlterModelOptions(
            name='cixwhitelist',
            options={'ordering': ['cidr']},
        ),
        migrations.AlterModelOptions(
            name='domain',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='image',
            options={'ordering': ['display_name']},
        ),
        migrations.AlterModelOptions(
            name='interface',
            options={'ordering': ['created']},
        ),
        migrations.AlterModelOptions(
            name='ipaddress',
            options={'ordering': ['address']},
        ),
        migrations.AlterModelOptions(
            name='ipmi',
            options={'ordering': ['created']},
        ),
        migrations.AlterModelOptions(
            name='poolip',
            options={'ordering': ['created']},
        ),
        migrations.AlterModelOptions(
            name='project',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='record',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='router',
            options={'ordering': ['region_id']},
        ),
        migrations.AlterModelOptions(
            name='server',
            options={'ordering': ['region_id']},
        ),
        migrations.AlterModelOptions(
            name='virtualrouter',
            options={'ordering': ['project__name']},
        ),
    ]
