## Onion Routing in SDN

> While the onion routing code is working fine, we were unable to get it to work properly consistently in Mininet due to some unknown error. The below steps are to run the project using Mininet. We have also given instructions on how to run onion routing part alone.

**Installation Steps:**

- Install MininetVM in [VirtualBox](https://www.virtualbox.org/). [Instructions here](http://mininet.org/vm-setup-notes/)

- Download the source code into the home directory and unzip it. 

- If the folder name is not named `acn_project`, rename it to `acn_project`. 

**Execution Steps:**

- `cd` into the directory and run `sudo python3 -E Topography.py`

- To start Tor Directory server, `xterm` out the host terminal(whichever host you want to run it on) and do `python3 ../acn_project/TorUsingSDN/SocketProgramming/TorDirectory.py <directory_port>`. The `<directory_port>` is the port at which the onion routing directory service listens.

- To start Tor Servers on other hosts, `xterm` out the host terminal and run `python3 ../acn_project/TorUsingSDN/SocketProgramming/TorServer.py <ip> <port> <dir_ip> <dir_port>`. `<ip>` is the IP address of the host. `<port>` is port at which the host needs to listen for Tor Service Requests. `<dir_ip>` and `<dir_port>` has to be IP and port of directory.

- To make an anonymous request, `xterm` out the host terminal and run `python3 ../acn_project/TorUsingSDN/SocketProgramming/TorClient.py <dir_ip> <dir_port>`


**Execution Steps for Pure Onion Routing:**

- Go to `Testing` folder in `TorUsingSDN` subdirectory. 
- Run the servers present in `Server1`, `Server2` and `Server3` respectively with command `python3 Torserver.py <port>` where `<port>` is the port at which the server needs to listen for servicing TOR requests.
- Run the client located in `Client` folder using the command `python3 TorClient.py`.
- You can select the option you want depending on your needs(either new identity or browsing)


**Screenshots**
