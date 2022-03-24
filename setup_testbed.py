import paramiko

from config import switch, username, server
from get_testbed_info import get_ip_mac, output
from pprint import pprint


def install_ovs(name, hostname, port):
    with open("ovs/ovs-setup.sh") as f:
        command = f.read()
    client = paramiko.SSHClient()
    try:
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname, port=port, username=username)
        print("Connecting {} {}:{}".format(name, hostname, port))
        _, stdout, _ = client.exec_command(command)
        output(stdout)

        cmd_add_br = "sudo ovs-vsctl --may-exist add-br {} && sudo ovs-vsctl list-br".format(name)
        _, stdout, _ = client.exec_command(cmd_add_br)
        output(stdout)
    except ... as e:
        print(e)
    finally:
        client.close()


def install_server(name, hostname, port):
    with open("server/server-setup.sh") as f:
        command = f.read()
    client = paramiko.SSHClient()
    try:
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname, port=port, username=username)
        print("Connecting {} {}:{}".format(name, hostname, port))
        _, stdout, _ = client.exec_command(command)
        output(stdout)
    except ... as e:
        print(e)
    finally:
        client.close()


def add_br_port(name, hostname, port, sw_list):
    client = paramiko.SSHClient()
    try:
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname, port=port, username=username)
        print("Connecting {} {}:{}".format(name, hostname, port))

        for node in sw_list:
            if node["name"] == name:
                for port in node["ports"]:
                    if port["name"] == "eth0":
                        continue
                    cmd_add_port = "sudo ovs-vsctl --may-exist add-port {} {}".format(name, port["name"])
                    _, stdout, _ = client.exec_command(cmd_add_port)
                    output(stdout)
                break

    except ... as e:
        print(e)
    finally:
        client.close()


if __name__ == "__main__":
    # for switch nodes
    # # install ovs
    for sw in switch:
        name = sw["name"]
        hostname = sw["hostname"]
        port = sw["port"]
        install_ovs(name, hostname, port)

    # # get ip mac pair
    sw_list = []
    for sw in switch:
        name = sw["name"]
        hostname = sw["hostname"]
        port = sw["port"]
        sw_list.append(get_ip_mac(name, hostname, port))

    # # add ovs br & port
    for sw in switch:
        name = sw["name"]
        hostname = sw["hostname"]
        port = sw["port"]
        add_br_port(name, hostname, port, sw_list)

    # for server node
    for s in server:
        name = s["name"]
        hostname = s["hostname"]
        port = s["port"]
        install_server(name, hostname, port)

    print("\nsave the following sw output")
    pprint(sw_list)
