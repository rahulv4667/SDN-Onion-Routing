from sys import stdout
from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
import asyncio
import os
import sys
from mininet.util import dumpNetConnections

DIRECTORY_PORT = 8000
SERVER_PORT = 9000
WEBSERVER_PORT = 8080

async def createNetwork(num_orgs, switches_per_org, hosts_per_switch):
    #os.chdir('/home/mininet/pox')
    net = Mininet(controller=RemoteController, switch=OVSSwitch, waitConnected=True, autoSetMacs=True)
    start_port = 6633
    org = 1
    controller_shells = list()
    ferror = open("ControllerLog.txt", "w")
    print('Creating network....')
    proc = await asyncio.create_subprocess_shell("""
            sudo pox-gar-wip3/pox.py log.level --DEBUG samples.pretty_log forwarding.l2_learning openflow.of_01 --port={}
         """.format(start_port+org), stdout=sys.stdout, stderr=ferror)
    c = net.addController('c%d'%org, port=start_port+org)
    for org in range(1, num_orgs+1):

        #controller_shells.append(proc)
        

        print('Created controller for {}'.format(org))
        
        #c = net.addController('c%d'%org, port=start_port+org, ip=f"10.{org}.0.0/16")
        
        for switch in range(1, switches_per_org+1):
            #s: OVSSwitch = net.addSwitch('s%d_%d'%(org, switch), ip=f"10.{org}.{switch}.0/24")
            s: OVSSwitch = net.addSwitch('s%d_%d'%(org, switch))
            print('Create switch {} - {}'.format(s.name, s.IP()))

            for host in range(1, hosts_per_switch+1):
                #h = net.addHost('h%d_%d_%d'%(org, switch, host), 
                #    ip=f"10.{org}.{switch}.{host}/24"
                #)
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
    #net.addNAT(name="nat0", flush=True).configDefault()
    return net, controller_shells

def initNetwork(net: Mininet):
    net.build()
    # for ctrlr in net.controllers:
    #     # ctrlr.start()
    #     print('*** Started controller {}'.format(ctrlr.name))

    #     for switch in net.switches:
    #         if switch.name.split('_')[0][1:] == ctrlr.name[1:]:
    #             switch.start([ctrlr])
    #             print('*** Started switch {} connected with controller {}'.format(switch.name, ctrlr.name))


    for switch in net.switches:
        switch.start([net.controllers[0]])
        print('*** Started switch {} connected with controller {}'.format(switch.name, net.controllers[0].name))
    
    directoryServerHost = net.hosts[0]
    directoryServerHost.cmd(f"python3 TorUsingSDN/SocketProgramming/TorDirectory.py {directoryServerHost.IP()} {DIRECTORY_PORT} &")
    print(f"Directory server Running at {directoryServerHost.IP()} {DIRECTORY_PORT}")
    
    # for host in net.hosts[1:8]:
    #     host.cmd(f"python3 TorUsingSDN/SocketProgramming/TorServer.py {host.IP()} {SERVER_PORT} {directoryServerHost.IP()} {DIRECTORY_PORT} &")
    
    webserver = net.hosts[-1]
    print(f"Web server is running at {webserver.IP()} {WEBSERVER_PORT}")
    webserver.cmd(f"python3 TorUsingSDN/SampleWebServer.py {webserver.IP()} {WEBSERVER_PORT} &")


def destroyNetwork(net: Mininet):
    for switch in net.switches:
        switch.stop()
    
    for ctrlr in net.controllers:
        ctrlr.stop()
    

if __name__ == "__main__":
    setLogLevel('info')
    f = open('netconf', 'r+')
    vals = f.readline()
    [num_orgs, num_switches, num_hosts] = vals.split()
    num_orgs = int(num_orgs.strip())
    num_switches = int(num_switches.strip())
    num_hosts = int(num_hosts.strip())

    print(num_orgs, num_switches, num_hosts)


    net, cshells = asyncio.run(createNetwork(num_orgs, num_switches, num_hosts))
    initNetwork(net)
    dumpNetConnections(net)
    net.start()
    CLI(net)
    destroyNetwork(net)

    for shell in cshells:
        shell.kill()