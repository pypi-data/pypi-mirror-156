from django import forms

from dcim.models import *
from netbox.forms import NetBoxModelForm
from utilities.forms import (
    BootstrapMixin, DynamicModelChoiceField, DynamicModelMultipleChoiceField, ExpandableNameField,
)

__all__ = (
    'ComponentTemplateCreateForm',
    'DeviceComponentCreateForm',
    'FrontPortCreateForm',
    'FrontPortTemplateCreateForm',
    'InventoryItemCreateForm',
    'ModularComponentTemplateCreateForm',
    'ModuleBayCreateForm',
    'ModuleBayTemplateCreateForm',
    'VirtualChassisCreateForm',
)


class ComponentCreateForm(BootstrapMixin, forms.Form):
    """
    Subclass this form when facilitating the creation of one or more device component or component templates based on
    a name pattern.
    """
    name_pattern = ExpandableNameField(
        label='Name'
    )
    label_pattern = ExpandableNameField(
        label='Label',
        required=False,
        help_text='Alphanumeric ranges are supported. (Must match the number of names being created.)'
    )

    def clean(self):
        super().clean()

        # Validate that all patterned fields generate an equal number of values
        patterned_fields = [
            field_name for field_name in self.fields if field_name.endswith('_pattern')
        ]
        pattern_count = len(self.cleaned_data['name_pattern'])
        for field_name in patterned_fields:
            value_count = len(self.cleaned_data[field_name])
            if self.cleaned_data[field_name] and value_count != pattern_count:
                raise forms.ValidationError({
                    field_name: f'The provided pattern specifies {value_count} values, but {pattern_count} are '
                                f'expected.'
                }, code='label_pattern_mismatch')


class ComponentTemplateCreateForm(ComponentCreateForm):
    """
    Creation form for component templates that can be assigned only to a DeviceType.
    """
    device_type = DynamicModelChoiceField(
        queryset=DeviceType.objects.all(),
    )
    field_order = ('device_type', 'name_pattern', 'label_pattern')


class ModularComponentTemplateCreateForm(ComponentCreateForm):
    """
    Creation form for component templates that can be assigned to either a DeviceType *or* a ModuleType.
    """
    device_type = DynamicModelChoiceField(
        queryset=DeviceType.objects.all(),
        required=False
    )
    module_type = DynamicModelChoiceField(
        queryset=ModuleType.objects.all(),
        required=False
    )
    field_order = ('device_type', 'module_type', 'name_pattern', 'label_pattern')


class DeviceComponentCreateForm(ComponentCreateForm):
    device = DynamicModelChoiceField(
        queryset=Device.objects.all()
    )
    field_order = ('device', 'name_pattern', 'label_pattern')


class FrontPortTemplateCreateForm(ModularComponentTemplateCreateForm):
    rear_port_set = forms.MultipleChoiceField(
        choices=[],
        label='Rear ports',
        help_text='Select one rear port assignment for each front port being created.',
    )
    field_order = (
        'device_type', 'name_pattern', 'label_pattern', 'rear_port_set',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # TODO: This needs better validation
        if 'device_type' in self.initial or self.data.get('device_type'):
            parent = DeviceType.objects.get(
                pk=self.initial.get('device_type') or self.data.get('device_type')
            )
        elif 'module_type' in self.initial or self.data.get('module_type'):
            parent = ModuleType.objects.get(
                pk=self.initial.get('module_type') or self.data.get('module_type')
            )
        else:
            return

        # Determine which rear port positions are occupied. These will be excluded from the list of available mappings.
        occupied_port_positions = [
            (front_port.rear_port_id, front_port.rear_port_position)
            for front_port in parent.frontporttemplates.all()
        ]

        # Populate rear port choices
        choices = []
        rear_ports = parent.rearporttemplates.all()
        for rear_port in rear_ports:
            for i in range(1, rear_port.positions + 1):
                if (rear_port.pk, i) not in occupied_port_positions:
                    choices.append(
                        ('{}:{}'.format(rear_port.pk, i), '{}:{}'.format(rear_port.name, i))
                    )
        self.fields['rear_port_set'].choices = choices

    def get_iterative_data(self, iteration):

        # Assign rear port and position from selected set
        rear_port, position = self.cleaned_data['rear_port_set'][iteration].split(':')

        return {
            'rear_port': int(rear_port),
            'rear_port_position': int(position),
        }


class FrontPortCreateForm(DeviceComponentCreateForm):
    rear_port_set = forms.MultipleChoiceField(
        choices=[],
        label='Rear ports',
        help_text='Select one rear port assignment for each front port being created.',
    )
    field_order = (
        'device', 'name_pattern', 'label_pattern', 'rear_port_set',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        device = Device.objects.get(
            pk=self.initial.get('device') or self.data.get('device')
        )

        # Determine which rear port positions are occupied. These will be excluded from the list of available
        # mappings.
        occupied_port_positions = [
            (front_port.rear_port_id, front_port.rear_port_position)
            for front_port in device.frontports.all()
        ]

        # Populate rear port choices
        choices = []
        rear_ports = RearPort.objects.filter(device=device)
        for rear_port in rear_ports:
            for i in range(1, rear_port.positions + 1):
                if (rear_port.pk, i) not in occupied_port_positions:
                    choices.append(
                        ('{}:{}'.format(rear_port.pk, i), '{}:{}'.format(rear_port.name, i))
                    )
        self.fields['rear_port_set'].choices = choices

    def get_iterative_data(self, iteration):

        # Assign rear port and position from selected set
        rear_port, position = self.cleaned_data['rear_port_set'][iteration].split(':')

        return {
            'rear_port': int(rear_port),
            'rear_port_position': int(position),
        }


class ModuleBayTemplateCreateForm(ComponentTemplateCreateForm):
    position_pattern = ExpandableNameField(
        label='Position',
        required=False,
        help_text='Alphanumeric ranges are supported. (Must match the number of names being created.)'
    )
    field_order = ('device_type', 'name_pattern', 'label_pattern', 'position_pattern')


class ModuleBayCreateForm(DeviceComponentCreateForm):
    position_pattern = ExpandableNameField(
        label='Position',
        required=False,
        help_text='Alphanumeric ranges are supported. (Must match the number of names being created.)'
    )
    field_order = ('device', 'name_pattern', 'label_pattern', 'position_pattern')


class InventoryItemCreateForm(ComponentCreateForm):
    # Device is assigned by the model form
    field_order = ('name_pattern', 'label_pattern')


class VirtualChassisCreateForm(NetBoxModelForm):
    region = DynamicModelChoiceField(
        queryset=Region.objects.all(),
        required=False,
        initial_params={
            'sites': '$site'
        }
    )
    site_group = DynamicModelChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        initial_params={
            'sites': '$site'
        }
    )
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        query_params={
            'region_id': '$region',
            'group_id': '$site_group',
        }
    )
    rack = DynamicModelChoiceField(
        queryset=Rack.objects.all(),
        required=False,
        null_option='None',
        query_params={
            'site_id': '$site'
        }
    )
    members = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False,
        query_params={
            'site_id': '$site',
            'rack_id': '$rack',
        }
    )
    initial_position = forms.IntegerField(
        initial=1,
        required=False,
        help_text='Position of the first member device. Increases by one for each additional member.'
    )

    class Meta:
        model = VirtualChassis
        fields = [
            'name', 'domain', 'region', 'site_group', 'site', 'rack', 'members', 'initial_position', 'tags',
        ]

    def clean(self):
        if self.cleaned_data['members'] and self.cleaned_data['initial_position'] is None:
            raise forms.ValidationError({
                'initial_position': "A position must be specified for the first VC member."
            })

    def save(self, *args, **kwargs):
        instance = super().save(*args, **kwargs)

        # Assign VC members
        if instance.pk and self.cleaned_data['members']:
            initial_position = self.cleaned_data.get('initial_position', 1)
            for i, member in enumerate(self.cleaned_data['members'], start=initial_position):
                member.virtual_chassis = instance
                member.vc_position = i
                member.save()

        return instance
