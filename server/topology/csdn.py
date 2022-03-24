"""
CSDN Topology

Topology used in "CSDN: CDN-Aware QoE Optimization in SDN-Assisted HTTP Adaptive Video Streaming"
"""

# Import the Portal object.
import geni.portal as portal
# Import the ProtoGENI library.
import geni.rspec.pg as pg

site_name = "sabr"
# ovs_image = "urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU18OVS"
# node_image = "urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU20-64-STD"
mask = "255.255.0.0"

# Create a portal object
pc = portal.Context()

# Create a Request object to start building the RSpec.
request = pc.makeRequestRSpec()

# Switch for origin server
sw_origin = request.XenVM("sw_origin")
# Switch for clients
client_sw = []
number_of_regions = 4
for i in range(number_of_regions):
    sw = request.XenVM("sw{}".format(i + 1))
    client_sw.append(sw)
    link = request.Link("link-origin-clientsw-{}".format(i + 1))
    link.Site(site_name)
    link.addInterface(
        sw.addInterface("ifsw-clientsw-{}".format(i + 1), pg.IPv4Address("10.10.254.{}".format(i + 1), mask)))
    link.addInterface(
        sw_origin.addInterface("ifsw-originsw-{}".format(i + 1), pg.IPv4Address("10.10.253.{}".format(i + 1), mask)))

# Origin server
node_server = request.XenVM('server')
# node_server.disk_image = node_image
if_server = node_server.addInterface('if-server', pg.IPv4Address('10.10.1.1', mask))
if_sw = sw_origin.addInterface(
    "ifsw-origin",
    pg.IPv4Address("10.10.1.253", mask)
)
link = request.Link("link-origin-server")
link.Site(site_name)
link.addInterface(if_sw)
link.addInterface(if_server)

# add clients for each region
number_of_client_each_region = 1
for i in range(number_of_regions):
    for j in range(number_of_client_each_region):
        client = request.XenVM("sw{}c{}".format(i + 1, j + 1))
        link = request.Link("link-sw{}c{}".format(i + 1, j + 1))
        link.Site(site_name)
        link.addInterface(
            client_sw[i].addInterface("ifsw-sw{}c{}".format(i + 1, j + 1),
                                      pg.IPv4Address("10.10.{}.{}".format(i + 1, j + 1), mask))
        )
        link.addInterface(
            client.addInterface("if-sw{}c{}".format(i + 1, j + 1),
                                pg.IPv4Address("10.10.{}.{}".format(i + 1 + 100, j + 1), mask))
        )

pc.printRequestRSpec(request)
