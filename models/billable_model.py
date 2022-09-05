# stdlib
from datetime import datetime
from typing import Callable, Dict, Tuple
# lib
from django.db import models
# local
from iaas import state

__all__ = ['BillableModelMixin']


class BillableModelMixin(models.Model):
    """
    Mixin class required for models to be picked up by the cloud bill api automatically

    Provides an override for .save that creates BOM entries.
    This save method assumes that the related name for BOM on the model is `skus`.
    THIS IS CRUCIAL OR THE AUTOMATION WILL NOT WORK.
    """
    skus: models.Model
    state: models.IntegerField
    updated: models.DateTimeField

    class Meta:
        # Make sure Django doesn't do anything with this class
        abstract = True

    def get_skus(self) -> Dict[str, Callable[[models.Model], int]]:  # pragma: no cover
        """
        Return a map of SKU titles to a function that will return the quantity to insert into the database if we need it
        """
        raise NotImplementedError('Abstract method `get_skus` needs to be defined on the subclass.')

    def get_label(self) -> str:  # pragma: no cover
        """
        Return a label to associate with the SKU quantities during the output.
        """
        raise NotImplementedError('Abstract method `label` needs to be defined on the subclass.')

    def save(self, *args, **kwargs):
        """
        Override save, creating BOM entries for the model using the functions as defined in this mixin
        """
        super(BillableModelMixin, self).save(*args, **kwargs)
        # Ignore if we're saving with a state we don't need to create BOMs for
        if self.state not in state.BOM_CREATE_STATES:
            return

        # If we are, make sure we have the latest information
        self.refresh_from_db()

        # Call the method to create SKU entries on the VM's updated date
        self.create_boms(self.updated)

    def create_boms(self, date: datetime):
        # Loop through the SKU Map field and insert BOM entries
        sku_map = self.get_skus()

        for sku, calc in sku_map.items():
            quantity = 0  # Assume we ignore, unless we need to call the function
            if self.state not in state.BILLING_IGNORE_STATES:
                quantity = calc(self)

            self.skus.create(
                sku=sku,
                quantity=quantity,
                created=date,
            )

    def get_sku_quantities(self, run_time: datetime) -> Dict[str, int]:
        """
        Generate the SKUs mapped to the number of item/hours to bill for
        """
        # Get all the BOMs for the VM ordered earliest to latest
        vm_boms = self.skus.filter(created__lte=run_time).order_by('created')
        # Create a map of each sku to the total number of item hours they have been used for
        # (this is the total overall quantity * time map that we will return)
        sku_totals: Dict[str, int] = {}
        # Also create a map for tracking sku states as we loop through the bom lines
        # {'HDD_001': (60, datetime.now())}
        sku_running_states: Dict[str, Tuple[int, datetime]] = {}

        for bom_line in vm_boms:
            sku = bom_line.sku

            # Initial population of the dictionaries
            if sku not in sku_totals:
                sku_totals[sku] = 0
                sku_running_states[sku] = (bom_line.quantity, bom_line.created)
                continue

            # If we reach this point, a SKU has been changed, so we need to do updates for it
            current_timestamp = bom_line.created
            prev_quantity, prev_timestamp = sku_running_states[sku]

            # Get the number of hours between this timestamp and the last, multiply the current quantity, update totals
            delta = current_timestamp - prev_timestamp
            hours = (delta.days * 24) + (delta.seconds // 3600)
            sku_totals[sku] += hours * prev_quantity

            # Update our running totals
            sku_running_states[sku] = (bom_line.quantity, current_timestamp)

        # At the end of the loop, we get the current time and do the time maths for the quantities in running_states
        for sku in sku_running_states:
            prev_quantity, prev_timestamp = sku_running_states[sku]
            delta = run_time - prev_timestamp
            hours = (delta.days * 24) + (delta.seconds // 3600)
            sku_totals[sku] += hours * prev_quantity

        return sku_totals
