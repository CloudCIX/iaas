# Generated by Django 2.2 on 2021-08-20 09:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iaas', '0014_snapshots'),
    ]

    operations = [
        migrations.AddField(
            model_name='snapshot',
            name='remove_subtree',
            field=models.BooleanField(default=False),
        ),
        migrations.AddIndex(
            model_name='snapshot',
            index=models.Index(fields=['remove_subtree'], name='snapshot_remove_subtree'),
        ),

        # Update fields with state 18 to state 99 (changed CLOSED state number)
        migrations.RunSQL("""
            UPDATE vm
            SET state = 99
            WHERE state = 18;
        """),

        migrations.RunSQL("""
            UPDATE vm_history
            SET state = 99
            WHERE state = 18;
        """),

        migrations.RunSQL("""
            UPDATE virtual_router
            SET state = 99
            WHERE state = 18;
        """),
    ]
