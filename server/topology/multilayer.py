"""
Multi layer Topology
"""

import geni.portal as portal
import geni.rspec.pg as pg

site_name = "multilayer"
mask = "255.0.0.0"

"""
IP for Origin Switch Ports:
10.254.254.x
10.254.253.x

IP for Interconnecting Backbone Switch Ports:
10.253.i.j
10.253.j.i
"""

# Create a portal object
pc = portal.Context()

# Create a Request object to start building the RSpec.
request = pc.makeRequestRSpec()

# Switch for origin server
sw_origin = request.XenVM("sw_origin")

# Backbone switch
backbone_sw = []
number_of_backbone_regions = 3
for i in range(number_of_backbone_regions):
    sw = request.XenVM("backbone_sw{}".format(i + 1))
    backbone_sw.append(sw)
    link = request.Link("l-ogsw-bbsw-{}".format(i + 1))
    link.Site(site_name)
    link.addInterface(
        sw.addInterface("if-bbsw-ogsw-{}".format(i + 1), pg.IPv4Address("10.254.254.{}".format(i + 1), mask)))
    link.addInterface(
        sw_origin.addInterface("if-ogsw-bbsw-{}".format(i + 1), pg.IPv4Address("10.254.253.{}".format(i + 1), mask)))

for i in range(len(backbone_sw)):
    for j in range(i+1, len(backbone_sw)):
        link = request.Link("l-sw{}-sw{}".format(i+1, j+1))
        link.Site(site_name)
        link.addInterface(backbone_sw[i].addInterface("if-sw{}-sw{}".format(i+1, j+1), pg.IPv4Address("10.253.{}.{}".format(i+1, j+1), mask)))
        link.addInterface(backbone_sw[j].addInterface("if-sw{}-sw{}".format(j+1, i+1), pg.IPv4Address("10.253.{}.{}".format(j+1, i+1), mask)))

# Origin server
node_server = request.RawPC('server')
if_sw = sw_origin.addInterface("if-ogsw-server", pg.IPv4Address("10.201.1.1", mask))
if_server = node_server.addInterface('if-server', pg.IPv4Address('10.1.1.1', mask))
link = request.Link("l-ogsw-server")
link.Site(site_name)
link.addInterface(if_sw)
link.addInterface(if_server)

# add clients and cache for each backbone region
number_of_client_each_region = 1
for i in range(number_of_backbone_regions):
    cache = request.XenVM("sw{}-cache".format(i+1))
    link = request.Link("l-sw{}-cache".format(i+1))
    link.Site(site_name)
    link.addInterface(backbone_sw[i].addInterface("if-sw{}-cache".format(i+1), pg.IPv4Address("10.210.{}.254".format(i+1), mask)))
    link.addInterface(cache.addInterface("if-cache-sw{}".format(i+1), pg.IPv4Address("10.10.{}.254".format(i+1), mask)))
    for j in range(number_of_client_each_region):
        client = request.XenVM("sw{}c{}".format(i + 1, j + 1))
        link = request.Link("l-sw{}c{}".format(i + 1, j + 1))
        link.Site(site_name)
        link.addInterface(
            backbone_sw[i].addInterface("if-sw{}c{}".format(i + 1, j + 1),
                                      pg.IPv4Address("10.210.{}.{}".format(i + 1, j + 1), mask))
        )
        link.addInterface(
            client.addInterface("if-c{}sw{}".format(j + 1, i + 1),
                                pg.IPv4Address("10.10.{}.{}".format(i + 1, j + 1), mask))
        )

remote_region_sw = request.XenVM("sw-r")
remote_clients = 4
for i in range(remote_clients):
    client = request.XenVM("sw-r-c{}".format(i + 1))
    link = request.Link("l-sw-r-c{}".format(i + 1))
    link.Site(site_name)
    link.addInterface(
        remote_region_sw.addInterface("if-sw-r-c{}".format(i + 1),
                                    pg.IPv4Address("10.210.200.{}".format(i + 1), mask))
    )
    link.addInterface(
        client.addInterface("if-c{}sw-r".format(i + 1),
                            pg.IPv4Address("10.10.200.{}".format(i + 1), mask))
    )

link = request.Link("l-sw-r-c")
link.Site(site_name)
link.addInterface(
    remote_region_sw.addInterface("if-sw-r-c", pg.IPv4Address("10.252.254.254", mask))
)
link.addInterface(
    backbone_sw[len(backbone_sw)-1].addInterface("if-c-sw-r", pg.IPv4Address("10.252.253.253", mask))
)

pc.printRequestRSpec(request)
