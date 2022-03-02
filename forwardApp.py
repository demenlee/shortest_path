# conding=utf-8

from ryu import ofproto
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ether_types
from ryu.lib.packet import ethernet, ipv4, arp
from ryu.lib import hub
from ryu.lib import dpid as dpid_lib
from ryu.topology.api import get_switch, get_link
from ryu.app import simple_switch_13
import networkx as nx

from setting import *

class ForwardApp(simple_switch_13.SimpleSwitch13):
    '''
    This a ryu app routing by the shortest path.
    '''
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *_args, **_kwargs):
        super(ForwardApp, self).__init__(*_args, **_kwargs)
        self.topology_api_app = self
        self.graph = graph
        # self.pre_graph = nx.DiGraph()

        self.datapaths = {}    # {dpid: datapath}

        self.path_to_outport = {}  # {dpid: {(src: dst): ouput}}
        self.pairs_to_paths = {}  # paths = {pair=(src_host, dst_host): path=[sw_dpid, ]}

    def create_flow_entries(self, datapath):
        for pair_host in self.pairs_to_paths:
            # pair_host = (hosts[pair_dpid[0]],hosts[pair_dpid[1]])  # dpid: 0-15
            p = self.pairs_to_paths[pair_host]
            for i in range(len(p)):
                # outport = datapath.ofproto.OFPP_LOCAL
                src_dpid = p[i]
                if i == len(p)-1:
                    outport = HostPort[src_dpid]
                else:  # i< len(p)-1
                    dst_dpid = p[i+1]
                    outport = linkDic[(src_dpid, dst_dpid)]
                if src_dpid in self.path_to_outport:
                    self.path_to_outport[src_dpid][pair_host] = outport
                else:
                    self.path_to_outport[src_dpid] = {pair_host: outport}

    def create_shortest_path(self, src_ip, dst_ip):
        src_dpid = satellites[src_ip]
        dst_dpid = satellites[dst_ip]
        path = nx.shortest_path(self.graph, src_dpid, dst_dpid)
        self.pairs_to_paths[(src_ip, dst_ip)] = path

    @set_ev_cls(ofp_event.EventOFPStateChange, [MAIN_DISPATCHER, DEAD_DISPATCHER])
    def _state_change_handler(self, ev):
        """
            Collect datapath information.  (Record datapath's info)
        """
        datapath = ev.datapath
        if ev.state == MAIN_DISPATCHER:
            if not datapath.id in self.datapaths:
                self.logger.debug('register datapath: %016x', datapath.id)
                self.datapaths[datapath.id] = datapath
        elif ev.state == DEAD_DISPATCHER:
            if datapath.id in self.datapaths:
                self.logger.debug('unregister datapath: %016x', datapath.id)
                del self.datapaths[datapath.id]

    def _build_packet_out(self, datapath, buffer_id, in_port, out_port, data):
        """
            Build packet out object.
        """
        actions = []
        if out_port:
            actions.append(datapath.ofproto_parser.OFPActionOutput(out_port))

        msg_data = None
        if buffer_id == datapath.ofproto.OFP_NO_BUFFER:
            if data is None:
                return None
            msg_data = data

        out = datapath.ofproto_parser.OFPPacketOut(datapath=datapath, buffer_id=buffer_id,
                                        data=msg_data, in_port=in_port, actions=actions)
        return out

    def send_packet_out(self, datapath, buffer_id, in_port, out_port, data):
        out = self._build_packet_out(datapath, buffer_id, in_port, out_port, data)
        if out:
            datapath.send_msg(out)

    def add_flow_mod(self, datapath, buffer_id, flow_info, parser, out_port, eth_type):
        self.logger.info("packet-in from switch%s %s %s in_port= %s out_port= %s", flow_info[0], flow_info[1], flow_info[2], flow_info[3], out_port)
        if eth_type == ether_types.ETH_TYPE_IP:
            match = parser.OFPMatch(in_port=flow_info[3], ipv4_src=flow_info[1], ipv4_dst=flow_info[2], eth_type=eth_type)
        elif eth_type == ether_types.ETH_TYPE_ARP:
            match = parser.OFPMatch(in_port=flow_info[3], arp_spa=flow_info[1], arp_tpa=flow_info[2], eth_type=eth_type)
        actions = [parser.OFPActionOutput(out_port)]
        if buffer_id != datapath.ofproto.OFP_NO_BUFFER:
            self.add_flow(datapath, 2, match, actions, buffer_id)
            return
        else:
            self.add_flow(datapath, 2, match, actions)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        dpid = dpid_lib.dpid_to_str(datapath.id) 
        self.logger.info("switch:%s connected", dpid)

        match = parser.OFPMatch()    # openflow packet match
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,       
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        if ev.msg.msg_len < ev.msg.total_len:
            self.logger.debug("packet truncated: only %s of %s bytes",
                              ev.msg.msg_len, ev.msg.total_len)
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']
        # dpid = dpid_lib.dpid_to_str(datapath.id)
        dpid = datapath.id
        data = msg.data

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]
        ip_pkt = pkt.get_protocol(ipv4.ipv4)
        arp_pkt = pkt.get_protocol(arp.arp)
        eth_type = eth.ethertype

        if eth_type == ether_types.ETH_TYPE_LLDP:
            self.logger.info("link discover protocol")
            return
        dst = eth.dst
        src = eth.src

        buffer_id = msg.buffer_id
        ip_src = None
        ip_dst = None
        if isinstance(arp_pkt, arp.arp):
            self.logger.info("ARP processing: orienteering forwarding")
            ip_src = arp_pkt.src_ip
            ip_dst = arp_pkt.dst_ip
            self.create_shortest_path(ip_src, ip_dst)
            self.create_flow_entries(datapath)
            out_port = self.path_to_outport[dpid][(ip_src, ip_dst)]
            self.logger.info("arp packet-in from switch%s %s %s %s %s", dpid, ip_src, ip_dst, in_port, out_port)  

            flow_info = (dpid, ip_src, ip_dst, in_port)
            self.add_flow_mod(datapath, buffer_id, flow_info, parser, out_port, eth_type)

            self.send_packet_out(datapath, buffer_id, in_port, out_port, data)


        if isinstance(ip_pkt, ipv4.ipv4):
            self.logger.info("IPV4 processing: install flow entry")
            ip_dst = ip_pkt.dst 
            ip_src = ip_pkt.src
            self.create_shortest_path(ip_src, ip_dst)
            self.create_flow_entries(datapath)
            out_port = self.path_to_outport[dpid][(ip_src, ip_dst)]
            self.logger.info("ipv4 packet-in from switch%s %s %s %s %s", dpid, ip_src, ip_dst, in_port, out_port)

            flow_info = (dpid, ip_src, ip_dst, in_port)
            self.add_flow_mod(datapath, buffer_id, flow_info, parser, out_port, eth_type)
            
            self.send_packet_out(datapath, buffer_id, in_port, out_port, data)


    

