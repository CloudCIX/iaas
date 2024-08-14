# stdlib
import json
# lib
from django.core.management.base import BaseCommand
# local
from iaas.models import (
    Image,
    ServerType,
    StorageType,
)


class Command(BaseCommand):
    can_import_settings = True
    help = (
        'A command to seed the database with the necessary CloudCIX supported infrastructure. '
    )

    def seed_constants(self):
        """
        Load the data contained in the seed_data json files into the DB
        """
        # Storage Type
        with open('iaas/management/commands/seed_data/storage_type.json') as f:
            data = json.load(f)
        for obj in data:
            try:
                storage_type = StorageType.objects.get(pk=obj['id'])
                storage_type.name = obj['name']
                storage_type.save()
            except StorageType.DoesNotExist:
                StorageType.objects.create(
                    pk=obj['id'],
                    name=obj['name'],
                )

        # Server Type
        with open('iaas/management/commands/seed_data/server_type.json') as f:
            data = json.load(f)
        for obj in data:
            try:
                server_type = ServerType.objects.get(pk=obj['id'])
                server_type.name = obj['name']
                server_type.save()
            except ServerType.DoesNotExist:
                ServerType.objects.create(
                    pk=obj['id'],
                    name=obj['name'],
                )

        # Image Method
        with open('iaas/management/commands/seed_data/image.json') as f:
            data = json.load(f)
        for obj in data:
            try:
                image = Image.objects.get(pk=obj['id'])
                image.answer_file_name = obj['answer_file_name']
                image.display_name = obj['display_name']
                image.filename = obj['filename']
                image.multiple_ips = obj['multiple_ips']
                image.os_variant = obj['os_variant']
                image.server_type_id = obj['server_type_id']
                image.save()
            except Image.DoesNotExist:
                Image.objects.create(
                    pk=obj['id'],
                    answer_file_name=obj['answer_file_name'],
                    display_name=obj['display_name'],
                    filename=obj['filename'],
                    multiple_ips=obj['multiple_ips'],
                    os_variant=obj['os_variant'],
                    server_type_id=obj['server_type_id'],
                )

    def handle(self, *args, **options):
        """
        Seed the iaas database with the necessary default records
        """
        self.seed_constants()
