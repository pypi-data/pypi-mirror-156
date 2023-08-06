from django import forms

from dcim.models import *
from extras.forms import CustomFieldsMixin
from extras.models import Tag
from utilities.forms import DynamicModelMultipleChoiceField, ExpandableNameField, form_from_model
from .object_create import ComponentCreateForm

__all__ = (
    'ConsolePortBulkCreateForm',
    'ConsoleServerPortBulkCreateForm',
    'DeviceBayBulkCreateForm',
    # 'FrontPortBulkCreateForm',
    'InterfaceBulkCreateForm',
    'InventoryItemBulkCreateForm',
    'ModuleBayBulkCreateForm',
    'PowerOutletBulkCreateForm',
    'PowerPortBulkCreateForm',
    'RearPortBulkCreateForm',
)


#
# Device components
#

class DeviceBulkAddComponentForm(CustomFieldsMixin, ComponentCreateForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=Device.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    description = forms.CharField(
        max_length=100,
        required=False
    )
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )


class ConsolePortBulkCreateForm(
    form_from_model(ConsolePort, ['type', 'speed', 'mark_connected']),
    DeviceBulkAddComponentForm
):
    model = ConsolePort
    field_order = ('name_pattern', 'label_pattern', 'type', 'mark_connected', 'description', 'tags')


class ConsoleServerPortBulkCreateForm(
    form_from_model(ConsoleServerPort, ['type', 'speed', 'mark_connected']),
    DeviceBulkAddComponentForm
):
    model = ConsoleServerPort
    field_order = ('name_pattern', 'label_pattern', 'type', 'speed', 'description', 'tags')


class PowerPortBulkCreateForm(
    form_from_model(PowerPort, ['type', 'maximum_draw', 'allocated_draw', 'mark_connected']),
    DeviceBulkAddComponentForm
):
    model = PowerPort
    field_order = ('name_pattern', 'label_pattern', 'type', 'maximum_draw', 'allocated_draw', 'description', 'tags')


class PowerOutletBulkCreateForm(
    form_from_model(PowerOutlet, ['type', 'feed_leg', 'mark_connected']),
    DeviceBulkAddComponentForm
):
    model = PowerOutlet
    field_order = ('name_pattern', 'label_pattern', 'type', 'feed_leg', 'description', 'tags')


class InterfaceBulkCreateForm(
    form_from_model(Interface, ['type', 'enabled', 'speed', 'duplex', 'mtu', 'mgmt_only', 'mark_connected']),
    DeviceBulkAddComponentForm
):
    model = Interface
    field_order = (
        'name_pattern', 'label_pattern', 'type', 'enabled', 'speed', 'duplex', 'mtu', 'mgmt_only', 'mark_connected', 'description', 'tags',
    )


# class FrontPortBulkCreateForm(
#     form_from_model(FrontPort, ['label', 'type', 'description', 'tags']),
#     DeviceBulkAddComponentForm
# ):
#     pass


class RearPortBulkCreateForm(
    form_from_model(RearPort, ['type', 'color', 'positions', 'mark_connected']),
    DeviceBulkAddComponentForm
):
    model = RearPort
    field_order = ('name_pattern', 'label_pattern', 'type', 'positions', 'mark_connected', 'description', 'tags')


class ModuleBayBulkCreateForm(DeviceBulkAddComponentForm):
    model = ModuleBay
    field_order = ('name_pattern', 'label_pattern', 'position_pattern', 'description', 'tags')

    position_pattern = ExpandableNameField(
        label='Position',
        required=False,
        help_text='Alphanumeric ranges are supported. (Must match the number of names being created.)'
    )


class DeviceBayBulkCreateForm(DeviceBulkAddComponentForm):
    model = DeviceBay
    field_order = ('name_pattern', 'label_pattern', 'description', 'tags')


class InventoryItemBulkCreateForm(
    form_from_model(InventoryItem, ['role', 'manufacturer', 'part_id', 'serial', 'asset_tag', 'discovered']),
    DeviceBulkAddComponentForm
):
    model = InventoryItem
    field_order = (
        'name_pattern', 'label_pattern', 'role', 'manufacturer', 'part_id', 'serial', 'asset_tag', 'discovered',
        'description', 'tags',
    )
