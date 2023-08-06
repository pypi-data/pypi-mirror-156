from .types import *


class Devices(NCSObject):

    _path = "/config/devices"

    _nsmap = {
            "config":"http://tail-f.com/ns/config/1.0",
            "devices":"http://tail-f.com/ns/ncs",
            }

    _xml_munge = {
        r'<ned-id>(.+)</ned-id>':'<ned-id xmlns:\g<1>="http://tail-f.com/ns/ned-id/\g<1>">\g<1></ned-id>'
    }

    def initialize_model(self):
        self.device = List(Device)
        self.device_group = List(DeviceGroup)

class Device(NCSObject):

    _path = "/config/devices/device"

    _nsmap = {
            "config":"http://tail-f.com/ns/config/1.0",
            "devices":"http://tail-f.com/ns/ncs",
            }

    _xml_munge = {
        r'<ned-id>(.+)</ned-id>':'<ned-id xmlns:\g<1>="http://tail-f.com/ns/ned-id/\g<1>">\g<1></ned-id>'
    }

    def initialize_model(self):

        self.name = Leaf(str)
        self.address = Leaf(str)
        self.authgroup = Leaf(str, value="default")
        self.device_role = Leaf(str)
        self.device_profile = Leaf(str)
        self.state = Container()
        self.state.admin_state = Leaf(str, value="unlocked")
        self.device_type = Container()
        self.device_type.ned_type = Choice(['cli','netconf'])
        self.device_type.ned_type.cli = Container()
        self.device_type.ned_type.netconf = Container()
        self.device_type.ned_type.cli.ned_id = Leaf(str)
        self.device_type.ned_type.netconf.ned_id = Leaf(str)
        self.in_band_mgmt = Container()
        self.in_band_mgmt.set_ns("http://umnet.umich.edu/umnetcommon")
        self.in_band_mgmt.ip_address = Leaf(str)
        self.in_band_mgmt.interface = Leaf(str)
        self.um_building = Container()
        self.um_building.set_ns("http://umnet.umich.edu/umnetcommon")
        self.um_building.building_no = Leaf(str)
        self.um_building.building_name = Leaf(str)
        self.um_building.building_address = Leaf(str)
        self.um_building.room_no = Leaf(str)
        self.um_building.floor = Leaf(str)


class DeviceGroup(NCSObject):

    _path = "/config/devices/device-group"

    _nsmap = {
            "config":"http://tail-f.com/ns/config/1.0",
            "devices":"http://tail-f.com/ns/ncs",
            }

    def initialize_model(self):
        self.name = Leaf(str)
        self.device_name = LeafList(str)


class Switchport(NCSObject):

    def initialize_model(self):

        self.name = Leaf(str)
        self.admin_state = Leaf(str)
        self.description = Leaf(str)
        self.speed_and_duplex = Leaf(str)
        
        self.mode = Container()
        self.mode.mode_choice = Choice(['access','trunk','default'])

        self.mode.mode_choice.access = Container()
        self.mode.mode_choice.access.vlan = Leaf(str)
        self.mode.mode_choice.access.voip_vlan = Leaf(str)
        self.mode.mode_choice.access.poe = Container(hide_if_empty=True)
        self.mode.mode_choice.access.poe.admin_state = Leaf(str)
        self.mode.mode_choice.access.poe.maximum_power = Leaf(str)
        self.mode.mode_choice.access.poe.priority = Leaf(str)

        self.mode.mode_choice.trunk = Container()
        self.mode.mode_choice.trunk.native_vlan = Leaf(str)
        self.mode.mode_choice.trunk.vlan_list = LeafList(str)
        self.mode.mode_choice.default = Container()


class IPv6Subnet(NCSObject):

    def initialize_model(self):
        self.prefix = Leaf(str)

class Network(NCSObject):

    _path = "/config/services/network"
    _nsmap = {
            "config":"http://tail-f.com/ns/config/1.0",
            "services":"http://tail-f.com/ns/ncs",
            "network":"http://example.com/umnet-network"
            }

    def initialize_model(self):

        self.name = Leaf(str)
        self.role = Leaf(str)
        self.description = Leaf(str)
        self.layer2 = Container()
        self.layer2.vlan_id = Leaf(int)

        self.layer3 = Container()
        self.layer3.vrf = Leaf(str)
        self.layer3.primary_ipv4_subnet = Leaf(str)
        self.layer3.secondary_ipv4_subnets = LeafList(str)
        self.layer3.ipv6_subnet = List(IPv6Subnet, keyattr="prefix")
        self.layer3.dhcp_relay_servers = Leaf(str)
        self.layer3.ingress_acl = Leaf(str)
        self.layer3.egress_acl = Leaf(str)

class Networks(NCSObject):

    _path = "/config/services"
    _nsmap = {
            "config":"http://tail-f.com/ns/config/1.0",
            "services":"http://tail-f.com/ns/ncs",
            }

    def initialize_model(self):

        self.network = List(Network)
        self.network.set_ns("http://umnet.umich.edu/umnet-network")

class NGFWVsyses(NCSObject):
    _path = "/config/services"
    _nsmap = {
            "config":"http://tail-f.com/ns/config/1.0",
            "services":"http://tail-f.com/ns/ncs",
            }
    def initialize_model(self):
        self.ngfw_vsys = List(NGFWVsys)
        self.ngfw_vsys.set_ns("http://umnet.umich.edu/umnet-vrf")

class NGFWVsys(NCSObject):

    def initialize_model(self):
        self.name = Leaf(str)
        self.asn = Leaf(str)
        
class Vrf(NCSObject):

    def initialize_model(self):

        self.name = Leaf('str')
        self.ngfw_vsys_or_vrf_asn = Choice(['ngfw-vsys', 'vrf-asn'])
        self.ngfw_vsys_or_vrf_asn.ngfw_vsys = Leaf(str)
        self.ngfw_vsys_or_vrf_asn.vrf_asn = Leaf(int)

        self.vrf_no = Leaf(int)

class Vrfs(NCSObject):

    _path = "/config/services"
    _nsmap = {
            "config":"http://tail-f.com/ns/config/1.0",
            "services":"http://tail-f.com/ns/ncs",
            }

    def initialize_model(self):
        self.vrf = List(Vrf)
        self.vrf.set_ns('http://umnet.umich.edu/umnet-vrf')

class BaseconfProfile(NCSObject):
    '''
    For the ncs migration project we don't actually
    profiles, we just need to be able to add devices to
    ones that already exist. As a result we're not defining
    any groups or profile details here.
    '''
    _nsmap = {
            "config":"http://tail-f.com/ns/config/1.0",
            "services":"http://tail-f.com/ns/ncs",
            "baseconf":"http://umnet.umich.edu/umnet-baseconf",
        }
        
    def initialize_model(self):
        self.name = Leaf(str)
        self.devices = LeafList(str)


class Baseconf(NCSObject):
    _path = "/config/services"
    _nsmap = {
            "config":"http://tail-f.com/ns/config/1.0",
            "services":"http://tail-f.com/ns/ncs",
            }

    _name = "baseconf"
    _ns = "http://umnet.umich.edu/umnet-baseconf"

    def initialize_model(self):
        self.profile = List(BaseconfProfile)



class Switch(NCSObject):
    def initialize_model(self):
        self.name = Leaf(str)
        self.switchport = List(Switchport)

class SwitchUplinks(NCSObject):
    def initialize_model(self):
        self.name = Leaf(str)
        self.uplink = List(Uplink)

class Uplink(NCSObject):

    def initialize_model(self):
        self.name = Leaf(str)
        self.uplink_type = Choice(['single-dl','al-to-al'])
        self.uplink_type.single_dl = Container()
        self.uplink_type.single_dl.pri_or_sec = Choice(['primary_router_ifname','secondary_router_ifname'])
        self.uplink_type.single_dl.pri_or_sec.primary_router_ifname = Leaf(str)
        self.uplink_type.single_dl.pri_or_sec.secondary_router_ifname = Leaf(str)

        self.uplink_type.al_to_al = Container()
        self.uplink_type.al_to_al.remote_switch = Leaf(str)
        self.uplink_type.al_to_al.remote_interface = Leaf(str)

class StaticRoute(NCSObject):

    def initialize_model(self):
        self.prefix = Leaf(str)
        self.next_hop = Leaf(str)
        self.priority = Leaf(str)

class DistNetwork(NCSObject):

    def initialize_model(self):
        self.name = Leaf(str)
        self.ipv4_static_route = List(StaticRoute, keyattr="prefix")
        self.ipv6_static_route = List(StaticRoute, keyattr="prefix")

class Distribution(NCSObject):

    _path = "/config/services/distribution"
    _nsmap = {
            "config":"http://tail-f.com/ns/config/1.0",
            "services":"http://tail-f.com/ns/ncs",
            "distribution":"http://umnet.umich.edu/distribution",
            }

    def initialize_model(self):

        self.name = Leaf(str)
        self.legacy_zone = Leaf(bool, True)
        self.fabric = Leaf(str)

        self.routing = Container(hide_if_empty=True)
        self.routing.network = List(DistNetwork)

        # note that because we're only dealing with legacy zones
        # right now, the primary/secondary DLs can be modeled
        # as switches.
        self.routing.primary_router = Switch(hide_if_empty=True)
        self.routing.secondary_router = Switch(hide_if_empty=True)

        self.switch = List(Switch)

        self.uplinks = Container(hide_if_empty=True)
        self.uplinks.switch = List(SwitchUplinks)

class DHCPServerGroup(NCSObject):

    def initialize_model(self):
        self.name = Leaf(str)
        self.server_ip = LeafList(str)

class Constants(NCSObject):
    
    _path = "/config/services/constants"
    _nsmap = {
            "config":"http://tail-f.com/ns/config/1.0",
            "services":"http://tail-f.com/ns/ncs",
            "constants":"http://umnet.umich.edu/constants",
    }

    def initialize_model(self):
        self.dhcp_server_group = List(DHCPServerGroup)


class CoreRouter(NCSObject):
    def initialize_model(self):
        self.device = Leaf(str)


class FabricRouter(NCSObject):
    def initialize_model(self):
        self.name = Leaf(str)
        self.core_loopback_address = Leaf(str)


class BgwRouter(NCSObject):
    def initialize_model(self):
        self.name = Leaf(str)
        self.nve_pip = Leaf(str)


class P2PLink(NCSObject):
    def initialize_model(self):
        self.name = Leaf(str)

        self.upstream = Container()
        self.upstream.device = Leaf(str)
        self.upstream.ifname = Leaf(str)

        self.downstream = Container()
        self.downstream.device = Leaf(str)
        self.downstream.ifname = Leaf(str)

        self.link_ipv4_prefix = Leaf(str)
        self.link_ipv6_prefix = Leaf(str)

        self.circuit_id = Leaf(str)


class CoreToFabric(NCSObject):
    def initialize_model(self):
        self.name = Leaf(str)
        self.p2p = List(P2PLink)


class Core(NCSObject):

    _path = "/config/services/core"
    _nsmap = {
        "config":"http://tail-f.com/ns/config/1.0",
        "services":"http://tail-f.com/ns/ncs",
        "core":"http://umnet.umich.edu/ns/core",
    }

    def initialize_model(self):
        self.as_number = Leaf(int)
        self.router = List(CoreRouter, keyattr="device")
        self.fabric = List(CoreToFabric, keyattr="name")


class Fabric(NCSObject):

    _path = "/config/services/fabric"
    _nsmap = {
        "config":"http://tail-f.com/ns/config/1.0",
        "services":"http://tail-f.com/ns/ncs",
        "fabric":"http://umnet.umich.edu/ns/fabric",
    }

    def initialize_model(self):
        self.name = Leaf(str)

        self.underlay = Container()
        self.underlay.devices = LeafList(str)
        self.underlay.p2p = List(P2PLink, keyattr="name")

        self.evpn_overlay = Container()
        self.evpn_overlay.as_number = Leaf(int)
        self.evpn_overlay.anycast_rp = Leaf(str)
        self.evpn_overlay.spine = List(FabricRouter, keyattr="name")
        self.evpn_overlay.multi_site = Container()
        self.evpn_overlay.multi_site.anycast_vip = Leaf(str)
        self.evpn_overlay.multi_site.bgw = List(BgwRouter, keyattr="name")
