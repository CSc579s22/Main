"""
Star Topology

One server, connected with many clients
For fairness testing
"""


# Import the Portal object.
import geni.portal as portal
# Import the ProtoGENI library.
import geni.rspec.pg as pg
# Import the Emulab specific extensions.
import geni.rspec.emulab as emulab

site_name = "sabr"
# ovs_image = "urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU18OVS"
# node_image = "urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU20-64-STD"
mask = "255.255.255.0"

# Create a portal object,
pc = portal.Context()

# Create a Request object to start building the RSpec.
request = pc.makeRequestRSpec()


# Node sw1
num_of_clients = 10
node_sw1 = request.XenVM('sw1')
# node_sw1.disk_image = ovs_image
iface = []
for i in range(num_of_clients):
    iface_sw = node_sw1.addInterface(
        "interface-sw-{}".format(i),
        pg.IPv4Address("10.10.10.{}".format(i+1), mask)
    )

    node_client = request.RawPC('sw1c{}'.format(i+1))
    # node_client.disk_image = node_image
    iface_client = node_client.addInterface('interface-sw1c{}-0'.format(i+1),
                                            pg.IPv4Address('10.10.10.{}'.format(i+1+100), mask))

    link = request.Link('link-sw1-sw1c{}'.format(i+1))
    link.Site(site_name)
    link.addInterface(iface_sw)
    link.addInterface(iface_client)

# Node server
node_server = request.XenVM('server')
# node_server.disk_image = node_image
iface_server = node_server.addInterface('interface-1', pg.IPv4Address('10.10.10.254', mask))
iface_sw = node_sw1.addInterface(
        "interface-sw-server",
        pg.IPv4Address("10.10.10.253", mask)
)
link = request.Link("link-sw1-server")
link.Site(site_name)
link.addInterface(iface_sw)
link.addInterface(iface_server)

# Print the generated rspec
pc.printRequestRSpec(request)
