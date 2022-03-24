"""Simple SABR"""

# Import the Portal object.
import geni.portal as portal
# Import the ProtoGENI library.
import geni.rspec.pg as pg
# Import the Emulab specific extensions.
import geni.rspec.emulab as emulab

site_name = "sabr"
ovs_image = "urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU18OVS"
node_image = "urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU20-64-STD"
mask = "255.255.255.0"

# Create a portal object,
pc = portal.Context()

# Create a Request object to start building the RSpec.
request = pc.makeRequestRSpec()

# Node server
node_server = request.RawPC('server')
node_server.disk_image = node_image
iface0 = node_server.addInterface('interface-1', pg.IPv4Address('10.10.10.11', mask))

# Node sw1
node_sw1 = request.XenVM('sw1')
node_sw1.disk_image = ovs_image
iface1 = node_sw1.addInterface('interface-0', pg.IPv4Address('10.10.10.1', mask))
iface2 = node_sw1.addInterface('interface-3', pg.IPv4Address('10.10.10.2', mask))
iface3 = node_sw1.addInterface('interface-9', pg.IPv4Address('10.10.10.3', mask))
iface4 = node_sw1.addInterface('interface-11', pg.IPv4Address('10.10.10.6', mask))

# Node sw1c1
node_sw1c1 = request.RawPC('sw1c1')
node_sw1c1.disk_image = node_image
iface5 = node_sw1c1.addInterface('interface-2', pg.IPv4Address('10.10.10.12', mask))

# Node sw2
node_sw2 = request.XenVM('sw2')
node_sw2.disk_image = ovs_image
iface6 = node_sw2.addInterface('interface-5', pg.IPv4Address('10.10.10.4', mask))
iface7 = node_sw2.addInterface('interface-7', pg.IPv4Address('10.10.10.5', mask))
iface8 = node_sw2.addInterface('interface-8', pg.IPv4Address('10.10.10.13', mask))
iface9 = node_sw2.addInterface('interface-13', pg.IPv4Address('10.10.10.7', mask))

# Node sw2c1
node_sw2c1 = request.RawPC('sw2c1')
node_sw2c1.disk_image = node_image
iface10 = node_sw2c1.addInterface('interface-4', pg.IPv4Address('10.10.10.14', mask))

# Node sw2c2
node_sw2c2 = request.RawPC('sw2c2')
node_sw2c2.disk_image = node_image
iface11 = node_sw2c2.addInterface('interface-6', pg.IPv4Address('10.10.10.15', mask))

# Node sw1c2
node_sw1c2 = request.RawPC('sw1c2')
node_sw1c2.disk_image = node_image
iface12 = node_sw1c2.addInterface('interface-10', pg.IPv4Address('10.10.10.16', mask))

# Node cache1
node_cache1 = request.RawPC('cache1')
node_cache1.disk_image = node_image
iface13 = node_cache1.addInterface('interface-12', pg.IPv4Address('10.10.10.17', mask))

# Link link-0
link_0 = request.Link('link-0')
link_0.Site(site_name)
link_0.addInterface(iface1)
link_0.addInterface(iface0)

# Link link-1
link_1 = request.Link('link-1')
link_1.Site(site_name)
link_1.addInterface(iface5)
link_1.addInterface(iface2)

# Link link-2
link_2 = request.Link('link-2')
link_2.Site(site_name)
link_2.addInterface(iface10)
link_2.addInterface(iface6)

# Link link-3
link_3 = request.Link('link-3')
link_3.Site(site_name)
link_3.addInterface(iface11)
link_3.addInterface(iface7)

# Link link-4
link_4 = request.Link('link-4')
link_4.Site(site_name)
link_4.addInterface(iface8)
link_4.addInterface(iface3)

# Link link-5
link_5 = request.Link('link-5')
link_5.Site(site_name)
link_5.addInterface(iface12)
link_5.addInterface(iface4)

# Link link-6
link_6 = request.Link('link-6')
link_6.Site(site_name)
link_6.addInterface(iface13)
link_6.addInterface(iface9)

# Print the generated rspec
pc.printRequestRSpec(request)
