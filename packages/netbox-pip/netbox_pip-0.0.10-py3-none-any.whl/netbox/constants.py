from collections import OrderedDict
from typing import Dict

from circuits.filtersets import CircuitFilterSet, ProviderFilterSet, ProviderNetworkFilterSet
from circuits.models import Circuit, ProviderNetwork, Provider
from circuits.tables import CircuitTable, ProviderNetworkTable, ProviderTable
from dcim.filtersets import (
    CableFilterSet, DeviceFilterSet, DeviceTypeFilterSet, LocationFilterSet, ModuleFilterSet, ModuleTypeFilterSet,
    PowerFeedFilterSet, RackFilterSet, RackReservationFilterSet, SiteFilterSet, VirtualChassisFilterSet,
)
from dcim.models import (
    Cable, Device, DeviceType, Location, Module, ModuleType, PowerFeed, Rack, RackReservation, Site, VirtualChassis,
)
from dcim.tables import (
    CableTable, DeviceTable, DeviceTypeTable, LocationTable, ModuleTable, ModuleTypeTable, PowerFeedTable, RackTable,
    RackReservationTable, SiteTable, VirtualChassisTable,
)
from ipam.filtersets import (
    AggregateFilterSet, ASNFilterSet, IPAddressFilterSet, PrefixFilterSet, VLANFilterSet, VRFFilterSet,
)
from ipam.models import Aggregate, ASN, IPAddress, Prefix, VLAN, VRF
from ipam.tables import AggregateTable, ASNTable, IPAddressTable, PrefixTable, VLANTable, VRFTable
from tenancy.filtersets import ContactFilterSet, TenantFilterSet
from tenancy.models import Contact, Tenant, ContactAssignment
from tenancy.tables import ContactTable, TenantTable
from utilities.utils import count_related
from virtualization.filtersets import ClusterFilterSet, VirtualMachineFilterSet
from virtualization.models import Cluster, VirtualMachine
from virtualization.tables import ClusterTable, VirtualMachineTable

SEARCH_MAX_RESULTS = 15

CIRCUIT_TYPES = OrderedDict(
    (
        ('provider', {
            'queryset': Provider.objects.annotate(
                count_circuits=count_related(Circuit, 'provider')
            ),
            'filterset': ProviderFilterSet,
            'table': ProviderTable,
            'url': 'circuits:provider_list',
        }),
        ('circuit', {
            'queryset': Circuit.objects.prefetch_related(
                'type', 'provider', 'tenant', 'terminations__site'
            ),
            'filterset': CircuitFilterSet,
            'table': CircuitTable,
            'url': 'circuits:circuit_list',
        }),
        ('providernetwork', {
            'queryset': ProviderNetwork.objects.prefetch_related('provider'),
            'filterset': ProviderNetworkFilterSet,
            'table': ProviderNetworkTable,
            'url': 'circuits:providernetwork_list',
        }),
    )
)


DCIM_TYPES = OrderedDict(
    (
        ('site', {
            'queryset': Site.objects.prefetch_related('region', 'tenant'),
            'filterset': SiteFilterSet,
            'table': SiteTable,
            'url': 'dcim:site_list',
        }),
        ('rack', {
            'queryset': Rack.objects.prefetch_related('site', 'location', 'tenant', 'role').annotate(
                device_count=count_related(Device, 'rack')
            ),
            'filterset': RackFilterSet,
            'table': RackTable,
            'url': 'dcim:rack_list',
        }),
        ('rackreservation', {
            'queryset': RackReservation.objects.prefetch_related('site', 'rack', 'user'),
            'filterset': RackReservationFilterSet,
            'table': RackReservationTable,
            'url': 'dcim:rackreservation_list',
        }),
        ('location', {
            'queryset': Location.objects.add_related_count(
                Location.objects.add_related_count(
                    Location.objects.all(),
                    Device,
                    'location',
                    'device_count',
                    cumulative=True
                ),
                Rack,
                'location',
                'rack_count',
                cumulative=True
            ).prefetch_related('site'),
            'filterset': LocationFilterSet,
            'table': LocationTable,
            'url': 'dcim:location_list',
        }),
        ('devicetype', {
            'queryset': DeviceType.objects.prefetch_related('manufacturer').annotate(
                instance_count=count_related(Device, 'device_type')
            ),
            'filterset': DeviceTypeFilterSet,
            'table': DeviceTypeTable,
            'url': 'dcim:devicetype_list',
        }),
        ('device', {
            'queryset': Device.objects.prefetch_related(
                'device_type__manufacturer', 'device_role', 'tenant', 'site', 'rack', 'primary_ip4', 'primary_ip6',
            ),
            'filterset': DeviceFilterSet,
            'table': DeviceTable,
            'url': 'dcim:device_list',
        }),
        ('moduletype', {
            'queryset': ModuleType.objects.prefetch_related('manufacturer').annotate(
                instance_count=count_related(Module, 'module_type')
            ),
            'filterset': ModuleTypeFilterSet,
            'table': ModuleTypeTable,
            'url': 'dcim:moduletype_list',
        }),
        ('module', {
            'queryset': Module.objects.prefetch_related(
                'module_type__manufacturer', 'device', 'module_bay',
            ),
            'filterset': ModuleFilterSet,
            'table': ModuleTable,
            'url': 'dcim:module_list',
        }),
        ('virtualchassis', {
            'queryset': VirtualChassis.objects.prefetch_related('master').annotate(
                member_count=count_related(Device, 'virtual_chassis')
            ),
            'filterset': VirtualChassisFilterSet,
            'table': VirtualChassisTable,
            'url': 'dcim:virtualchassis_list',
        }),
        ('cable', {
            'queryset': Cable.objects.all(),
            'filterset': CableFilterSet,
            'table': CableTable,
            'url': 'dcim:cable_list',
        }),
        ('powerfeed', {
            'queryset': PowerFeed.objects.all(),
            'filterset': PowerFeedFilterSet,
            'table': PowerFeedTable,
            'url': 'dcim:powerfeed_list',
        }),
    )
)

IPAM_TYPES = OrderedDict(
    (
        ('vrf', {
            'queryset': VRF.objects.prefetch_related('tenant'),
            'filterset': VRFFilterSet,
            'table': VRFTable,
            'url': 'ipam:vrf_list',
        }),
        ('aggregate', {
            'queryset': Aggregate.objects.prefetch_related('rir'),
            'filterset': AggregateFilterSet,
            'table': AggregateTable,
            'url': 'ipam:aggregate_list',
        }),
        ('prefix', {
            'queryset': Prefix.objects.prefetch_related('site', 'vrf__tenant', 'tenant', 'vlan', 'role'),
            'filterset': PrefixFilterSet,
            'table': PrefixTable,
            'url': 'ipam:prefix_list',
        }),
        ('ipaddress', {
            'queryset': IPAddress.objects.prefetch_related('vrf__tenant', 'tenant'),
            'filterset': IPAddressFilterSet,
            'table': IPAddressTable,
            'url': 'ipam:ipaddress_list',
        }),
        ('vlan', {
            'queryset': VLAN.objects.prefetch_related('site', 'group', 'tenant', 'role'),
            'filterset': VLANFilterSet,
            'table': VLANTable,
            'url': 'ipam:vlan_list',
        }),
        ('asn', {
            'queryset': ASN.objects.prefetch_related('rir', 'tenant'),
            'filterset': ASNFilterSet,
            'table': ASNTable,
            'url': 'ipam:asn_list',
        }),
    )
)

TENANCY_TYPES = OrderedDict(
    (
        ('tenant', {
            'queryset': Tenant.objects.prefetch_related('group'),
            'filterset': TenantFilterSet,
            'table': TenantTable,
            'url': 'tenancy:tenant_list',
        }),
        ('contact', {
            'queryset': Contact.objects.prefetch_related('group', 'assignments').annotate(
                assignment_count=count_related(ContactAssignment, 'contact')),
            'filterset': ContactFilterSet,
            'table': ContactTable,
            'url': 'tenancy:contact_list',
        }),
    )
)

VIRTUALIZATION_TYPES = OrderedDict(
    (
        ('cluster', {
            'queryset': Cluster.objects.prefetch_related('type', 'group').annotate(
                device_count=count_related(Device, 'cluster'),
                vm_count=count_related(VirtualMachine, 'cluster')
            ),
            'filterset': ClusterFilterSet,
            'table': ClusterTable,
            'url': 'virtualization:cluster_list',
        }),
        ('virtualmachine', {
            'queryset': VirtualMachine.objects.prefetch_related(
                'cluster', 'tenant', 'platform', 'primary_ip4', 'primary_ip6',
            ),
            'filterset': VirtualMachineFilterSet,
            'table': VirtualMachineTable,
            'url': 'virtualization:virtualmachine_list',
        }),
    )
)

SEARCH_TYPE_HIERARCHY = OrderedDict(
    (
        ("Circuits", CIRCUIT_TYPES),
        ("DCIM", DCIM_TYPES),
        ("IPAM", IPAM_TYPES),
        ("Tenancy", TENANCY_TYPES),
        ("Virtualization", VIRTUALIZATION_TYPES),
    )
)


def build_search_types() -> Dict[str, Dict]:
    result = dict()

    for app_types in SEARCH_TYPE_HIERARCHY.values():
        for name, items in app_types.items():
            result[name] = items

    return result


SEARCH_TYPES = build_search_types()
