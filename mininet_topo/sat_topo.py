#!/usr/bin/python
"""
This is a simple satellite topology to showcase Containernet.
"""
from re import S
from mininet.net import Containernet, Mininet
from mininet.node import Controller, RemoteController, Node, Switch
from mininet.cli import CLI
from mininet.link import TCLink, TCULink, TCIntf
from mininet.log import info, setLogLevel
from mininet.util import quietRun
import os

setLogLevel('info')

net = Containernet(controller=RemoteController)
info('*** Adding controller\n')
net.addController('c0')

info('*** Adding switches\n')      
sat_name = locals()
for i in range(16):
    sat_name['sat' + str(i)] = net.addSwitch('s'+str(i+1))

info('*** Adding docker containers\n')
'''
master = net.addDocker('master', ip='10.0.0.200', ports=['50070', '8088', '9000'] , 
                       dimage="demenlee/hadoop:v3.2.master", mac='00:00:00:00:00:20')
h1 = net.addDocker('slave1', ip='10.0.0.201', dimage="demenlee/hadoop:v3.2", mac='00:00:00:00:00:21')
'''
str_hosts = []
str_ips = []
last_ip = 200
mac_adrs = []
last_mac = 0
host_name = locals()
for i in range(16):
    str_hosts.append('h' + str(i+1))
    last_ip += 1
    last_str = str(last_ip)
    str_ips.append('10.0.0.' + last_str)
    last_mac += 1
    last_str = str(last_mac)
    mac_adrs.append('00:00:00:00:00:' + last_str)
    host_name['h' + str(i)] = net.addDocker(str_hosts[i], ip=str_ips[i], dimage="demenlee/hadoop:v3.2.master", mac=mac_adrs[i])



    
info('*** Creating links\n')
#net.addLink(master, s1, params1={"ip": "10.0.0.1/8"})
'''
net.addLink(sat1_1, sat1_2, cls=TCLink, delay='20ms', bw=100)
net.addLink(sat1_1, sat2_1, cls=TCLink, delay='5ms', bw=150)
'''
links = locals()
index = 0
for i in range(0,3):
    links['link'+str(index)] = net.addLink(sat_name['sat' + str(i)], sat_name['sat' + str(i+1)], cls=TCLink, delay='10ms', bw=100)
    index += 1
for i in range(4,7):
    links['link'+str(index)] = net.addLink(sat_name['sat' + str(i)], sat_name['sat' + str(i+1)], cls=TCLink, delay='10ms', bw=100)
    index += 1
for i in range(8,11):
    links['link'+str(index)] = net.addLink(sat_name['sat' + str(i)], sat_name['sat' + str(i+1)], cls=TCLink, delay='10ms', bw=100)
    index += 1
for i in range(12,15):
    links['link'+str(index)] = net.addLink(sat_name['sat' + str(i)], sat_name['sat' + str(i+1)], cls=TCLink, delay='10ms', bw=100)
    index += 1
for i in range(0,12,4):
    links['link'+str(index)] = net.addLink(sat_name['sat' + str(i)], sat_name['sat' + str(i+4)], cls=TCLink, delay='10ms', bw=100)
    index += 1
for i in range(1,13,4):
    links['link'+str(index)] = net.addLink(sat_name['sat' + str(i)], sat_name['sat' + str(i+4)], cls=TCLink, delay='10ms', bw=100)
    index += 1
for i in range(2,14,4):
    links['link'+str(index)] = net.addLink(sat_name['sat' + str(i)], sat_name['sat' + str(i+4)], cls=TCLink, delay='10ms', bw=100)
    index += 1
for i in range(3,15,4):
    links['link'+str(index)] = net.addLink(sat_name['sat' + str(i)], sat_name['sat' + str(i+4)], cls=TCLink, delay='10ms', bw=100)
    index += 1
#net.addLink(s12, s13, cls=TCLink, delay='10ms', bw=100)
for i in range(16):
    links['link'+str(index)] = net.addLink(sat_name['sat' + str(i)], host_name['h' + str(i)])
    index += 1

info('*** Starting network\n')
net.start()

info('*** Running CLI\n')
CLI(net)

info('\n*** Preparing to change links bw and delay\n')
while True:
    key = input("please input a num: 1 change links delay and bw, other is break: ")
    if key == '1':
        try:
            delay = input("please input delay ms ")
            bw = int(input("please input bw "))
            info('*** Changing links bw and delay\n')
            for i in range(0, 12):
                links['link' + str(i)].intf1.config(delay=delay, bw=bw)
                links['link' + str(i)].intf2.config(delay=delay, bw=bw)
            info('\n*** Running CLI\n')
            CLI(net)
        except:
            info("*** wrong input for delay and bw")
    else:
        break

info('*** Running CLI\n')
CLI(net)
info('*** Stopping network')
net.stop()