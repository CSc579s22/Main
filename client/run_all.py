import multiprocessing

import paramiko

from config import username, node
from server.config import NodeList


client_path = "/proj/QoESDN/AStream/dist/client/dash_client.py"
playback_command = "sudo python2 {} -t BigBuckBunny -c 10.10.10.1:8080 -p {} -i {}"
clean_cmd = "sudo rm -rf /proj/QoESDN/AStream/ASTREAM_LOGS"
node_name_list_to_test = ["sw-r-c1", "sw-r-c2", "sw-r-c3", "sw-r-c4"]
alg = "netflix"


def output(out):
    while True:
        line = out.readline()
        if not line:
            return
        print(line, end="")


def run_all():
    pool = multiprocessing.Pool(len(node_name_list_to_test))
    nodes = [n for n in NodeList if n["name"] in node_name_list_to_test]
    for n in nodes:
        hostname = ""
        port = ""
        for nn in node:
            if nn["name"] == n["name"]:
                hostname = nn["hostname"]
                port = nn["port"]
                break
        pool.apply_async(run_one, (n["name"], hostname, port, n["ip"], alg))
    pool.close()
    pool.join()


def run_one(name, hostname, port, local_ip, playback_alg):
    client = paramiko.SSHClient()
    try:
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname, port=port, username=username)
        print("Connecting {} {}:{}\n".format(name, hostname, port))
        # delete previous logs
        _, stdout, _ = client.exec_command(clean_cmd)

        # run one
        cmd = playback_command.format(client_path, playback_alg, local_ip)
        _, stdout, _ = client.exec_command(cmd)
        output(stdout)
    except ... as e:
        print(e)
    finally:
        client.close()


if __name__ == "__main__":
    run_all()
