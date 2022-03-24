import paramiko
from config import switch, username, node, cache, server
from pprint import pprint
from validate_topo import get_node_port_ip_on_sw


def output(out):
    while True:
        line = out.readline()
        if not line:
            return
        print(line, end="")


def get_ip_mac(name, hostname, port):
    """
    Example output
    Set the variable `Switch` in server/config.py as the output

[{'dpid': '00000a89a2b96340',
  'name': 'sw1',
  'ports': [{'hwaddr': '02:7a:d5:6f:bb:a2', 'ip': '10.253.1.3', 'name': 'eth1'},
            {'hwaddr': '02:f1:db:d1:1c:2e', 'ip': '10.253.1.2', 'name': 'eth2'},
            {'hwaddr': '02:49:0d:5e:17:d9',
             'ip': '10.210.1.254',
             'name': 'eth3'},
            {'hwaddr': '02:16:e1:c4:2e:3a', 'ip': '10.210.1.1', 'name': 'eth4'},
            {'hwaddr': '02:87:50:29:39:c2',
             'ip': '10.254.254.1',
             'name': 'eth5'}]},
 {'dpid': '000026bfef5c774a',
  'name': 'sw2',
  'ports': [{'hwaddr': '02:46:d2:90:a1:70',
             'ip': '10.210.2.254',
             'name': 'eth1'},
            {'hwaddr': '02:5c:17:70:d6:3f', 'ip': '10.253.2.3', 'name': 'eth2'},
            {'hwaddr': '02:93:95:e2:ed:29', 'ip': '10.210.2.1', 'name': 'eth3'},
            {'hwaddr': '02:e5:f3:45:dd:86', 'ip': '10.253.2.1', 'name': 'eth4'},
            {'hwaddr': '02:c0:b8:ec:fa:88',
             'ip': '10.254.254.2',
             'name': 'eth5'}]},
 {'dpid': '0000b6b0703ed649',
  'name': 'sw3',
  'ports': [{'hwaddr': '02:39:54:ad:bb:a9', 'ip': '10.253.3.1', 'name': 'eth1'},
            {'hwaddr': '02:07:58:70:65:05',
             'ip': '10.254.254.3',
             'name': 'eth2'},
            {'hwaddr': '02:af:b7:bc:7c:02',
             'ip': '10.252.253.253',
             'name': 'eth3'},
            {'hwaddr': '02:19:f3:ed:b2:12', 'ip': '10.253.3.2', 'name': 'eth4'},
            {'hwaddr': '02:06:51:8b:a5:aa',
             'ip': '10.210.3.254',
             'name': 'eth5'},
            {'hwaddr': '02:38:40:a9:a5:8a',
             'ip': '10.210.3.1',
             'name': 'eth6'}]},
 {'dpid': '00006a45c9ebe445',
  'name': 'sw-r',
  'ports': [{'hwaddr': '02:df:98:20:cc:9a', 'ip': '', 'name': 'eth1'},
            {'hwaddr': '02:78:b7:d2:29:f0', 'ip': '', 'name': 'eth2'},
            {'hwaddr': '02:8c:1a:a6:93:f2', 'ip': '', 'name': 'eth3'},
            {'hwaddr': '02:47:61:0d:7b:aa', 'ip': '', 'name': 'eth4'},
            {'hwaddr': '02:a8:f6:3a:12:b6', 'ip': '', 'name': 'eth5'}]},
 {'dpid': '0000b6d267844745',
  'name': 'sw-origin',
  'ports': [{'hwaddr': '02:43:6c:24:81:d8',
             'ip': '10.254.253.3',
             'name': 'eth1'},
            {'hwaddr': '02:a8:99:7c:da:ce', 'ip': '10.201.1.1', 'name': 'eth2'},
            {'hwaddr': '02:34:23:6f:d0:c8',
             'ip': '10.254.253.1',
             'name': 'eth3'},
            {'hwaddr': '02:17:66:38:b0:a2',
             'ip': '10.254.253.2',
             'name': 'eth4'}]}]
    """
    client = paramiko.SSHClient()
    try:
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname, port=port, username=username)
        print("Connecting {} {}:{}".format(name, hostname, port))

        cmd_list_if = "ls /sys/class/net"
        _, stdout, _ = client.exec_command(cmd_list_if)
        interfaces = stdout.read().decode("utf-8").split("\n")
        # print(interfaces)

        cmd_get_dpid = "sudo ovs-ofctl show %s | grep dpid | awk -F ':' '{print $3}'" % name
        _, stdout, _ = client.exec_command(cmd_get_dpid)
        dpid = stdout.read().decode("utf-8").strip("\n")
        node = {
            "name": name,
            "dpid": dpid,
            "ports": []
        }
        for iface in interfaces:
            if str.startswith(iface, "eth") and iface != "eth0":
                cmd_list_ip = "ip addr show %s | grep inet | grep %s | awk '{print $2}'" % (iface, iface)
                _, stdout, _ = client.exec_command(cmd_list_ip)
                ip = stdout.read().decode("utf-8").strip("\n").split("/")[0]

                cmd_list_mac = "ip link show %s | grep 'link/ether' | awk '{print $2}'" % iface
                _, stdout, _ = client.exec_command(cmd_list_mac)
                mac = stdout.read().decode("utf-8").strip("\n")

                print("{} {} {}".format(name, ip, mac))
                node["ports"].append(
                    {
                        "ip": ip,
                        "hwaddr": mac,
                        "name": iface,
                    }
                )
        return node
    except ... as e:
        print(e)
    finally:
        client.close()


def get_node_ovs_ip(name, hostname, port):
    client = paramiko.SSHClient()
    try:
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname, port=port, username=username)
        print("Connecting {} {}:{}".format(name, hostname, port))

        cmd_list_if = "ls /sys/class/net"
        _, stdout, _ = client.exec_command(cmd_list_if)
        interfaces = stdout.read().decode("utf-8").split("\n")

        for iface in interfaces:
            if iface != "eth0":
                cmd_list_ip = "ip addr show %s | grep inet | grep %s | awk '{print $2}'" % (iface, iface)
                _, stdout, _ = client.exec_command(cmd_list_ip)
                ip = stdout.read().decode("utf-8").strip("\n").split("/")[0]
                if str.startswith(ip, "10."):
                    cmd_list_mac = "ip link show %s | grep 'link/ether' | awk '{print $2}'" % iface
                    _, stdout, _ = client.exec_command(cmd_list_mac)
                    mac = stdout.read().decode("utf-8").strip("\n")

                    print("{} {} {}".format(name, ip, mac))
                    return ip, mac
        return node
    except ... as e:
        print(e)
    finally:
        client.close()


def get_mac_by_ip(name, hostname, port, ip_input):
    client = paramiko.SSHClient()
    try:
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname, port=port, username=username)
        # print("Connecting {} {}:{}".format(name, hostname, port))

        cmd_list_if = "ls /sys/class/net"
        _, stdout, _ = client.exec_command(cmd_list_if)
        interfaces = stdout.read().decode("utf-8").split("\n")

        for iface in interfaces:
            if iface != "eth0":
                cmd_list_ip = "ip addr show %s | grep inet | grep %s | awk '{print $2}'" % (iface, iface)
                _, stdout, _ = client.exec_command(cmd_list_ip)
                ip = stdout.read().decode("utf-8").strip("\n").split("/")[0]
                if ip == ip_input:
                    cmd_list_mac = "ip link show %s | grep 'link/ether' | awk '{print $2}'" % iface
                    _, stdout, _ = client.exec_command(cmd_list_mac)
                    mac = stdout.read().decode("utf-8").strip("\n")
                    return mac
    except ... as e:
        print(e)
    finally:
        client.close()


def get_node_list():
    all_nodes = []
    topo_filename = "topo.xml"
    for n in server+node:
        ip, mac = get_node_ovs_ip(n["name"], n["hostname"], n["port"])
        sw_node, port_ip = get_node_port_ip_on_sw(topo_filename, n["name"], ip)
        port_hwaddr = ""
        for sw in switch:
            if sw["name"] == sw_node:
                port_hwaddr = get_mac_by_ip(sw["name"], sw["hostname"], sw["port"], port_ip)
                break
        n_dict = {
            "ip": ip,
            "name": n["name"],
            "hwaddr": mac,
            "port": port_hwaddr
        }
        all_nodes.append(n_dict)

    for n in cache:
        ip, mac = get_node_ovs_ip(n["name"], n["hostname"], n["port"])
        sw_node, port_ip = get_node_port_ip_on_sw(topo_filename, n["name"], ip)
        port_hwaddr = ""
        for sw in switch:
            if sw["name"] == sw_node:
                port_hwaddr = get_mac_by_ip(sw["name"], sw["hostname"], sw["port"], port_ip)
                break
        n_dict = {
            "ip": ip,
            "name": n["name"],
            "hwaddr": mac,
            "port": port_hwaddr,
            "cache": True,
        }
        all_nodes.append(n_dict)

    return all_nodes


if __name__ == "__main__":
    all_node_info = get_node_list()
    print("\nsave the following node output")
    pprint(all_node_info)
