from mininet.log import setLogLevel
from mininet.node import RemoteController
from mininet.topo import Topo
from mininet.net import Mininet 
from mininet.cli import CLI
from mininet.util import dumpNodeConnections, dumpNetConnections, dumpPorts
import subprocess
import os

def createNetwork(orgs, hosts_per_switch, switches_per_org):
    os.chdir("/home/mininet/pox")
    start_port = 6633
    nets = list()

    for org in range(1, orgs+1):
        # os.system("""
        # sudo ~/pox/pox.py misc.acn_project.org_controller openflow.of_01 --port={} \
        #      samples.pretty_log log.level --DEBUG
        # """.format(start_port+org))

        os.system("""
            sudo ~/pox/pox.py misc.acn_project.org_controller openflow.of_01 --port={}
        """.format(start_port+org))

        net = Mininet()
        net.addController(controller=RemoteController(port=start_port+org))
        for switch in range(1, switches_per_org+1):
            s = net.addSwitch('s%d_%d'%(start_port+org, switch))
            for host in range(1, hosts_per_switch):
                h = net.addHost('h%d_%d_%d'%(start_port+org, switch, host))
                net.addLink(s, h)
        nets.append(net)
                


if __name__ == "__main__":
    setLogLevel('info')
    f = open('/home/mininet/pox/pox/misc/acn_project/netconf', 'r+')
    vals = f.readline()
    [num_orgs, num_hosts, num_switches] = vals.split()
    num_orgs = int(num_orgs.strip())
    num_hosts = int(num_hosts.strip())
    num_switches = int(num_switches.strip())

    print(num_orgs)
    print(num_hosts)
    print(num_switches)
    nets = createNetwork(num_orgs, num_hosts, num_switches)

    for i, net in enumerate(nets):
        print('Starting network%d ...'%i)
        net.start()
        print('=============================')
        dumpNetConnections(net)
        print('==============================')
        # CLI(net)

        # print('Stopping network%d ... '%i)
        # net.stop()

    continue_loop = True
    while continue_loop:
        input_cmd = input()

        if input_cmd == 'exit':
            continue_loop = False

    for net in nets:
        print('Stopping network%d ...'%i)
        net.stop()