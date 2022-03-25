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
    print("\nupdate `NodeList` in server/config.py using the information printed")
    pprint(all_node_info)
