# stdlib
from typing import Optional
# libs
from cloudcix_rest.controllers import ControllerBase
# local
from iaas.models import Server, ServerType, StorageType

__all__ = [
    'ServerCreateController',
    'ServerListController',
    'ServerUpdateController',
]


class ServerListController(ControllerBase):
    """
    Validates Server data used to filter a list of Servers
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields
        """
        allowed_ordering = (
            'region_id',
            'asset_tag',
            'created',
            'enabled',
            'model',
            'type__name',
        )
        search_fields = {
            'asset_tag': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'cores': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'created': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'enabled': (),
            'gb': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'model': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'ram': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'region_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'storage_type__name': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'type__name': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'updated': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
        }


class ServerCreateController(ControllerBase):
    """
    Validates Server data used to create a new Server
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields
        """
        model = Server
        validation_order = (
            'type_id',
            'asset_tag',
            'enabled',
            'model',
            'ram',
            'cores',
            'storage_type_id',
            'gb',
        )

    def validate_type_id(self, type_id: Optional[int]) -> Optional[str]:
        """
        description: ID of the ServerType record that represents the type of Server that the new Server will be.
        type: integer
        """
        if type_id is None:
            return 'iaas_server_create_101'

        try:
            type_id = int(type_id)
        except (ValueError, TypeError):
            return 'iaas_server_create_102'

        try:
            obj = ServerType.objects.get(pk=type_id)
        except ServerType.DoesNotExist:
            return 'iaas_server_create_103'

        self.cleaned_data['type'] = obj
        return None

    def validate_asset_tag(self, asset_tag: Optional[int]) -> Optional[str]:
        """
        description: CloudCIX Asset Tag for the Server. Optional.
        required: false
        type: integer
        """
        if asset_tag is None:
            return None

        try:
            asset_tag = int(asset_tag)
        except (TypeError, ValueError):
            return 'iaas_server_create_104'

        self.cleaned_data['asset_tag'] = asset_tag
        return None

    def validate_enabled(self, enabled: Optional[bool]) -> Optional[str]:
        """
        description: Flag stating whether the host is currently accepting VMs. Default is True.
        type: boolean
        """
        if enabled is None:
            enabled = True

        if enabled not in {True, False}:
            return 'iaas_server_create_105'

        self.cleaned_data['enabled'] = enabled
        return None

    def validate_model(self, model: Optional[str]) -> Optional[str]:
        """
        description: Name of the model of the Server. Optional.
        type: string
        """
        if not model:
            return None
        model = str(model).strip()

        if len(model) > self.get_field('model').max_length:
            return 'iaas_server_create_106'

        self.cleaned_data['model'] = model
        return None

    def validate_ram(self, ram: Optional[int]) -> Optional[str]:
        """
        description: Total amount of RAM in the Server, in GB.
        type: integer
        """
        if not ram:
            return 'iaas_server_create_107'

        try:
            ram = int(ram)
        except (TypeError, ValueError):
            return 'iaas_server_create_108'

        if ram <= 0:
            return 'iaas_server_create_109'

        self.cleaned_data['ram'] = ram
        return None

    def validate_cores(self, cores: Optional[int]) -> Optional[str]:
        """
        description: Total number of physical cores in the Server.
        type: integer
        """
        if not cores:
            return 'iaas_server_create_110'

        try:
            cores = int(cores)
        except (TypeError, ValueError):
            return 'iaas_server_create_111'

        if cores <= 0:
            return 'iaas_server_create_112'

        self.cleaned_data['cores'] = cores
        return None

    def validate_storage_type_id(self, storage_type_id: Optional[int]) -> Optional[str]:
        """
        description: The ID of the StorageType that will be used in the Server.
        type: integer
        """
        if not storage_type_id:
            return 'iaas_server_create_113'

        try:
            storage_type_id = int(storage_type_id)
        except (ValueError, TypeError):
            return 'iaas_server_create_114'

        try:
            storage_type = StorageType.objects.get(pk=storage_type_id)
        except StorageType.DoesNotExist:
            return 'iaas_server_create_115'

        self.cleaned_data['storage_type'] = storage_type
        return None

    def validate_gb(self, gb: Optional[int]) -> Optional[str]:
        """
        description: The amount of GB that is usable in the Server for the Cloud. Must be more than 100 GB.
        type: integer
        """
        if gb is None:
            return 'iaas_server_create_116'

        try:
            gb = int(gb)
        except (TypeError, ValueError):
            return 'iaas_server_create_117'

        if gb < 100:
            return 'iaas_server_create_118'

        self.cleaned_data['gb'] = gb
        return None


class ServerUpdateController(ControllerBase):
    """
    Validates Server data used to update a Server
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields
        """
        model = Server
        validation_order = (
            'asset_tag',
            'cores',
            'enabled',
            'gb',
            'model',
            'ram',
            'storage_type_id',
            'type_id',
        )

    def validate_asset_tag(self, asset_tag: Optional[int]) -> Optional[str]:
        """
        description: CloudCIX Asset Tag for the Server. Optional.
        required: false
        type: integer
        """
        if asset_tag is None:
            return None

        try:
            asset_tag = int(asset_tag)
        except (TypeError, ValueError):
            return 'iaas_server_update_101'

        self.cleaned_data['asset_tag'] = asset_tag
        return None

    def validate_cores(self, cores: Optional[int]) -> Optional[str]:
        """
        description: Total number of physical cores in the Server.
        type: integer
        """
        if not cores:
            return None
        try:
            cores = int(cores)
        except (TypeError, ValueError):
            return 'iaas_server_update_102'

        if cores <= 0:
            return 'iaas_server_update_103'

        self.cleaned_data['cores'] = cores
        return None

    def validate_enabled(self, enabled: Optional[bool]) -> Optional[str]:
        """
        description: Flag stating whether the host is currently accepting VMs. Default is True.
        type: boolean
        """
        if enabled is None:
            return None

        if enabled not in {True, False}:
            return 'iaas_server_update_104'

        self.cleaned_data['enabled'] = enabled
        return None

    def validate_gb(self, gb: Optional[int]) -> Optional[str]:
        """
        description: The amount of GB that is usable in the Server for the Cloud. Must be more than 100 GB.
        type: integer
        """
        if not gb:
            return None

        try:
            gb = int(gb)
        except (TypeError, ValueError):
            return 'iaas_server_update_105'

        if gb < 100:
            return 'iaas_server_update_106'

        self.cleaned_data['gb'] = gb
        return None

    def validate_model(self, model: Optional[str]) -> Optional[str]:
        """
        description: Name of the model of the Server. Optional.
        type: string
        """
        if not model:
            return None
        model = str(model).strip()

        if len(model) > self.get_field('model').max_length:
            return 'iaas_server_update_107'

        self.cleaned_data['model'] = model
        return None

    def validate_ram(self, ram: Optional[int]) -> Optional[str]:
        """
        description: Total amount of RAM in the Server, in GB.
        type: integer
        """
        if ram is None:
            return None

        try:
            ram = int(ram)
        except (TypeError, ValueError):
            return 'iaas_server_update_108'

        if ram <= 0:
            return 'iaas_server_update_109'

        self.cleaned_data['ram'] = ram
        return None

    def validate_storage_type_id(self, storage_type_id: Optional[int]) -> Optional[str]:
        """
        description: The ID of the StorageType that will be used in the Server.
        type: integer
        """
        if storage_type_id is None:
            return None

        try:
            storage_type_id = int(storage_type_id)
        except (ValueError, TypeError):
            return 'iaas_server_update_110'

        try:
            storage_type = StorageType.objects.get(pk=storage_type_id)
        except StorageType.DoesNotExist:
            return 'iaas_server_update_111'

        self.cleaned_data['storage_type'] = storage_type
        return None

    def validate_type_id(self, type_id: Optional[int]) -> Optional[str]:
        """
        description: ID of the ServerType record that represents the type of Server that the new Server will be.
        type: integer
        """
        if type_id is None:
            return None
        try:
            type_id = int(type_id)
        except (ValueError, TypeError):
            return 'iaas_server_update_112'

        try:
            obj = ServerType.objects.get(pk=type_id)
        except ServerType.DoesNotExist:
            return 'iaas_server_update_113'

        self.cleaned_data['type'] = obj
        return None
