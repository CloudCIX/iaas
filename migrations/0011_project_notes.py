from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iaas', '0010_routes'),
    ]

    operations = [

        migrations.AddField(
            model_name='project',
            name='note',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='vm',
            name='public_key',
            field=models.TextField(null=True),
        ),

    ]
