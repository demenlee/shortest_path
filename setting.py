# Common Setting for sat_topology network, such as topo_graph, period et al.

import networkx as nx
# from matplotlib import pyplot as plt

PERIOD = 20   # For monitoring traffic (s) 

'''
dpids = ('0000000000000001', '0000000000000002', '0000000000000003', '0000000000000004', 
         '0000000000000005', '0000000000000006', '0000000000000007', '0000000000000008',
         '0000000000000009', '000000000000000a', '000000000000000b', '000000000000000c',
         '000000000000000d', '000000000000000e', '000000000000000f', '0000000000000010',)
'''
# switches_dpid list ， 不带端口号
dpids = [1, 2, 3, 4, 
          5, 6, 7, 8,
          9, 10, 11, 12,
          13, 14, 15, 16]

# hosts_ip list
hosts = ('10.0.0.201', '10.0.0.202', '10.0.0.203', '10.0.0.204',
         '10.0.0.205', '10.0.0.206', '10.0.0.207', '10.0.0.208',
         '10.0.0.209', '10.0.0.210', '10.0.0.211', '10.0.0.212',
         '10.0.0.213', '10.0.0.214', '10.0.0.215', '10.0.0.216')

# switch对应host的端口
HostPort = {dpids[0]:3,dpids[1]:4,dpids[2]:4,dpids[3]:3,
            dpids[4]:4,dpids[5]:5,dpids[6]:5,dpids[7]:4,
            dpids[8]:4,dpids[9]:5,dpids[10]:5,dpids[11]:4,
            dpids[12]:3,dpids[13]:4,dpids[14]:4,dpids[15]:3}

# {host_ip: dpid}
satellites = {hosts[0]: 1, hosts[1]: 2, hosts[2]: 3, hosts[3]: 4, 
              hosts[4]: 5, hosts[5]: 6, hosts[6]: 7, hosts[7]: 8, 
              hosts[8]: 9, hosts[9]: 10, hosts[10]: 11, hosts[11]: 12,
              hosts[12]: 13, hosts[13]: 14, hosts[14]: 15, hosts[15]: 16}


links = [(1, 2, {'port': (1, 1)}), (2, 3, {'port': (2, 1)}), (3, 4, {'port': (2, 1)}),
         (5, 6, {'port': (1, 1)}), (6, 7, {'port': (2, 1)}), (7, 8, {'port': (2, 1)}),
         (9, 10, {'port': (1, 1)}), (10, 11, {'port': (2, 1)}), (11, 12, {'port': (2, 1)}),
         (13, 14, {'port': (1, 1)}), (14, 15, {'port': (2, 1)}), (15, 16, {'port': (2, 1)}),
         (1, 5, {'port': (2, 2)}), (5, 9, {'port': (3, 2)}), (9, 13, {'port': (3, 2)}),
         (2, 6, {'port': (3, 3)}), (6, 10, {'port': (4, 3)}), (10, 14, {'port': (4, 3)}),
         (3, 7, {'port': (3, 3)}), (7, 11, {'port': (4, 3)}), (11, 15, {'port': (4, 3)}),
         (4, 8, {'port': (2, 2)}), (8, 12, {'port': (3, 2)}), (12, 16, {'port': (3, 2)})]

linkDic = {}  # {(src_dpid, dst_dpid): src_sw_port, }
for l in links:
    linkDic[(l[0],l[1])] = l[2]["port"][0]
    linkDic[(l[1],l[0])] = l[2]["port"][1]


graph = nx.Graph()
graph.add_nodes_from(dpids)
graph.add_edges_from(links)