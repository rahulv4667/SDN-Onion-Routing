from sys import stdout
from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
import asyncio
import os

from mininet.util import dumpNetConnections

DIRECTORY_PORT = 8000
SERVER_PORT = 8001

async def createNetwork(num_orgs, switches_per_org, hosts_per_switch):
    os.chdir('/home/mininet/pox')
    net = Mininet(controller=RemoteController, switch=OVSSwitch, waitConnected=True)
    start_port = 6633
    controller_shells = list()

    print('Creating network....')

    # proc = await asyncio.create_subprocess_shell("""
    #     sudo /home/mininet/pox/pox.py forwarding.l2_multi openflow.discovery openflow.of_01 --port={}
    # """.format(7000), stdout=stdout, stderr=asyncio.subprocess.PIPE)
    # controller_shells.append(proc)
    # dir_ctrlr = net.addController('c0', port=7000)
    # dir_switch = net.addSwitch('s0')
    # dir_server = net.addHost('h0')
    # net.addLink(dir_switch, dir_server)

    for org in range(1, num_orgs+1):
        # proc = await asyncio.create_subprocess_shell("""
        #     sudo /home/mininet/pox/pox.py org_controller openflow.of_01 --port={} \
        #         samples.pretty_log log.level --DEBUG
        # """.format(start_port+org), stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        proc = await asyncio.create_subprocess_shell("""
            sudo /home/mininet/pox/pox.py forwarding.l2_multi openflow.discovery openflow.of_01 --port={}
        """.format(start_port+org), stdout=stdout, stderr=asyncio.subprocess.PIPE)
        controller_shells.append(proc)
        

        print('Created controller for {}'.format(org))
        # c = net.addController(controller=RemoteController('c%d'%org, port=start_port+org))
        c = net.addController('c%d'%org, port=start_port+org)

        for switch in range(1, switches_per_org+1):
            s: OVSSwitch = net.addSwitch('s%d_%d'%(org, switch))
            print('Create switch {} - {}'.format(s.name, s.IP()))
            for host in range(1, hosts_per_switch+1):
                h = net.addHost('h%d_%d_%d'%(org, switch, host))
                net.addLink(s, h)
                print('Created host {} - {}'.format(h.name, h.IP()))
                print('Created a link between {} and {}'.format(s.name, h.name))
                if switch > 1:
                    prev_switch = net.getNodeByName('s%d_%d'%(org, switch-1))
                    print('Connections between {} and {} :::::=> {}'.format(
                        prev_switch.name,
                        s.name,
                        s.connectionsTo(prev_switch)
                    ))
                    if len(s.connectionsTo(prev_switch)) > 0:
                        continue
                    net.addLink(s, prev_switch)
                    print('Creaetd a link between {} and {}'.format(s.name, prev_switch.name))
    
    # connecting a switch of on org to switch of another org
    for i in range(1, num_orgs):
        s1 = net.getNodeByName('s%d_%d'%(i, switches_per_org))
        s2 = net.getNodeByName('s%d_%d'%((i+1)%(num_orgs+1), switches_per_org))
        net.addLink(s1, s2)
        # print('Created host {} - {}'.format(h.name, h.IP()))
        print('Created a link between {} and {}'.format(s1.name, s2.name))

    
    # s = net.getNodeByName('s1_1')
    # net.addLink(dir_switch, s)

    # for org in range(1, num_orgs+1):
    #     s = net.getNodeByName('s%d_1'%org)
    #     net.addLink(dir_switch, s)

    return net, controller_shells

def initNetwork(net: Mininet):
    net.build()
    
    # dir_ctrlr = net.getNodeByName('c0')
    # # dir_ctrlr.start()
    # dir_switch = net.getNodeByName('s0')
    # dir_switch.start([dir_ctrlr])
    # dir_server = net.getNodeByName('h0')
    # dir_server.cmd('python3 ../acn_project/TorUsingSDN/SocketProgramming/TorDirectory.py')
    # print('should have started directory service')
    
    for ctrlr in net.controllers:
        # ctrlr.start()
        print('*** Started controller {}'.format(ctrlr.name))

        for switch in net.switches:
            if switch.name.split('_')[0][1:] == ctrlr.name[1:]:
                switch.start([ctrlr])
                print('*** Started switch {} connected with controller {}'.format(switch.name, ctrlr.name))
        

    # dir_server = net.getNodeByName('h1_1_1')
    # dir_server.cmd("python3 ../acn_project/TorUsingSDN/SocketProgramming/TorDirectory.py %d &"%DIRECTORY_PORT)
    # print('should have started directory')        

    # for host in net.hosts:
    #     host.cmd("python3 ../acn_project/TorUsingSDN/SocketProgramming/TorServer.py %d %d &"%(
    #         SERVER_PORT,
    #         DIRECTORY_PORT
    #     ))


def destroyNetwork(net: Mininet):
    for switch in net.switches:
        switch.stop()
    
    for ctrlr in net.controllers:
        ctrlr.stop()
    

if __name__ == "__main__":
    setLogLevel('info')
    f = open('/home/mininet/acn_project/netconf', 'r+')
    vals = f.readline()
    [num_orgs, num_switches, num_hosts] = vals.split()
    num_orgs = int(num_orgs.strip())
    num_switches = int(num_switches.strip())
    num_hosts = int(num_hosts.strip())

    print(num_orgs, num_switches, num_hosts)


    net, cshells = asyncio.run(createNetwork(num_orgs, num_switches, num_hosts))
    initNetwork(net)
    dumpNetConnections(net)
    # net.pingAll()
    CLI(net)
    destroyNetwork(net)

    for shell in cshells:
        shell.terminate()