import queue
import threading
from prettytable import PrettyTable
import collections
import json


# wrapper class for a queue of packets
class Interface:
    # @param maxsize - the maximum size of the queue storing packets
    def __init__(self, maxsize=0):
        self.in_queue = queue.Queue(maxsize)
        self.out_queue = queue.Queue(maxsize)
    
    # get packet from the queue interface
    # @param in_or_out - use 'in' or 'out' interface
    def get(self, in_or_out):
        try:
            if in_or_out == 'in':
                pkt_S = self.in_queue.get(False)
                # if pkt_S is not None:
                #     print('getting packet from the IN queue')
                return pkt_S
            else:
                pkt_S = self.out_queue.get(False)
                # if pkt_S is not None:
                #     print('getting packet from the OUT queue')
                return pkt_S
        except queue.Empty:
            return None
        
    # put the packet into the interface queue
    # @param pkt - Packet to be inserted into the queue
    # @param in_or_out - use 'in' or 'out' interface
    # @param block - if True, block until room in queue, if False may throw queue.Full exception
    def put(self, pkt, in_or_out, block=False):
        if in_or_out == 'out':
            # print('putting packet in the OUT queue')
            self.out_queue.put(pkt, block)
        else:
            # print('putting packet in the IN queue')
            self.in_queue.put(pkt, block)
            
        
# Implements a network layer packet.
class NetworkPacket:
    # packet encoding lengths 
    dst_S_length = 5
    prot_S_length = 1
    
    # @param dst: address of the destination host
    # @param data_S: packet payload
    # @param prot_S: upper layer protocol for the packet (data, or control)
    def __init__(self, dst, prot_S, data_S):
        self.dst = dst
        self.data_S = data_S
        self.prot_S = prot_S
        
    # called when printing the object
    def __str__(self):
        return self.to_byte_S()
        
    # convert packet to a byte string for transmission over links
    def to_byte_S(self):
        byte_S = str(self.dst).zfill(self.dst_S_length)
        if self.prot_S == 'data':
            byte_S += '1'
        elif self.prot_S == 'control':
            byte_S += '2'
        else:
            raise('%s: unknown prot_S option: %s' %(self, self.prot_S))
        byte_S += self.data_S
        return byte_S
    
    # extract a packet object from a byte string
    # @param byte_S: byte string representation of the packet
    @classmethod
    def from_byte_S(self, byte_S):
        dst = byte_S[0 : NetworkPacket.dst_S_length].strip('0')
        prot_S = byte_S[NetworkPacket.dst_S_length : NetworkPacket.dst_S_length + NetworkPacket.prot_S_length]
        if prot_S == '1':
            prot_S = 'data'
        elif prot_S == '2':
            prot_S = 'control'
        else:
            raise('%s: unknown prot_S field: %s' %(self, prot_S))
        data_S = byte_S[NetworkPacket.dst_S_length + NetworkPacket.prot_S_length : ]        
        return self(dst, prot_S, data_S)


# Implements a network host for receiving and transmitting data
class Host:
    
    # @param addr: address of this node represented as an integer
    def __init__(self, addr):
        self.addr = addr
        self.intf_L = [Interface()]
        self.stop = False  # for thread termination
    
    # called when printing the object
    def __str__(self):
        return self.addr
       
    # create a packet and enqueue for transmission
    # @param dst: destination address for the packet
    # @param data_S: data being transmitted to the network layer
    def udt_send(self, dst, data_S):
        p = NetworkPacket(dst, 'data', data_S)
        print('%s: sending packet "%s"' % (self, p))
        self.intf_L[0].put(p.to_byte_S(), 'out')  # send packets always enqueued successfully
        
    # receive packet from the network layer
    def udt_receive(self):
        pkt_S = self.intf_L[0].get('in')
        if pkt_S is not None:
            print('%s: received packet "%s"' % (self, pkt_S))
       
    # thread target for the host to keep receiving data
    def run(self):
        print (threading.currentThread().getName() + ': Starting')
        while True:
            # receive data arriving to the in interface
            self.udt_receive()
            # terminate
            if self.stop:
                print(threading.currentThread().getName() + ': Ending')
                return
        

# Implements a multi-interface router
class Router:
    
    # @param name: friendly router name for debugging
    # @param cost_D: cost table to neighbors {neighbor: {interface: cost}}
    # @param max_queue_size: max queue length (passed to Interface)
    def __init__(self, name, cost_D, max_queue_size):
        self.stop = False  # for thread termination
        self.name = name
        self.was_updated = False
        # create a list of interfaces
        self.intf_L = [Interface(max_queue_size) for _ in range(len(cost_D))]
        # save neighbors and interfeces on which we connect to them
        self.cost_D = cost_D    # {neighbor: {interface: cost}}
        self.rt_tbl_D = {self.name: {self.name: 0}}      # {destination: {router: cost}}
        self.all_costs_D = {self.name: self.rt_tbl_D}
        self.set_rt_tbl()
        print('%s: Initialized routing table' % self)
        self.print_routes()

    def set_rt_tbl(self):
        for key, v1 in self.cost_D.items():
            for k2, v2 in v1.items():
                if key[0:1] == 'R':
                    self.rt_tbl_D[key] = {key: v2}
                else:
                    self.rt_tbl_D[key] = {self.name: v2}

    # Use costs to create routing table
    def update_route_table(self):
        table = PrettyTable([self.name])
        headers_L = []
        rows_L = []
        dist_D = {}  # Key is router, value is list of all costs associated with router
        order_routers = collections.OrderedDict(sorted(self.all_costs_D.items()))  # Order router by name
        for router, v1 in order_routers.items():
            dist_L = []
            if router not in rows_L:
                rows_L.append(router)
            order_vertices = collections.OrderedDict(sorted(v1.items()))  # Order of costs by destination name
            for vertex, v2 in order_vertices.items():
                dist_L.append(list(v2.values())[0])
                if vertex not in headers_L:
                    headers_L.append(vertex)
            dist_D[router] = dist_L
        # Create header row of table
        for i in headers_L:
            table.add_column(i, '')
        # fill table by rows
        for key, value in dist_D.items():
            data = [key]
            for n in value:
                data.append(n)
            table.add_row(data)
        return table

    # Print routing table
    def print_routes(self):
        print(self.update_route_table())
        print('\nThis is the full table as stored in dictionary form:\n')
        print(self.all_costs_D)
        print()

    # called when printing the object
    def __str__(self):
        return self.name

    # look through the content of incoming interfaces and 
    # process data and control packets
    def process_queues(self):
        for i in range(len(self.intf_L)):
            pkt_S = None
            # get packet from interface i
            pkt_S = self.intf_L[i].get('in')
            # if packet exists make a forwarding decision
            if pkt_S is not None:
                p = NetworkPacket.from_byte_S(pkt_S)  # parse a packet out
                if p.prot_S == 'data':
                    self.forward_packet(p, i)
                elif p.prot_S == 'control':
                    self.update_routes(p, i)
                else:
                    raise Exception('%s: Unknown packet type in packet %s' % (self, p))
            
    # forward the packet according to the routing table
    #  @param p Packet to forward
    #  @param i Incoming interface number for packet p
    def forward_packet(self, p, i):
        try:
            # TODO: Here you will need to implement a lookup into the 
            # forwarding table to find the appropriate outgoing interface
            # for now we assume the outgoing interface is 1
            self.intf_L[1].put(p.to_byte_S(), 'out', True)
            print('%s: forwarding packet "%s" from interface %d to %d' % \
                (self, p, i, 1))
        except queue.Full:
            print('%s: packet "%s" lost on interface %d' % (self, p, i))
            pass

    # send out route update
    # @param i Interface number on which to send out a routing update
    def send_routes(self, i):
        for v in self.rt_tbl_D:
            # Only broadcast route updates to neighbor routers, not hosts. Assumes that all routers will start with 'R'
            if v[0:1] == 'R' and v != self.name:
                p = NetworkPacket(v, 'control', self.name + json.dumps(self.rt_tbl_D))
                try:
                    print('%s: sending routing update "%s" from interface %d' % (self, p, i))
                    self.intf_L[i].put(p.to_byte_S(), 'out', True)
                except queue.Full:
                    print('%s: packet "%s" lost on interface %d' % (self, p, i))
                    pass
        self.was_updated = False  # Reset flag to acknowledge update was broadcast

    # Bellman-Ford Distance Vector Algorithm to find shortest path based on neighbor router cost update
    # @param router Vertex that sent the update
    # @param update_D Route update to be integrated
    def bellman_ford(self, router, update_D):
        dist_router = self.rt_tbl_D[router][router]
        for vertex in update_D:
            if self.name == vertex:
                continue
            else:
                # Add previously unknown vertex to map
                if vertex not in self.rt_tbl_D:
                    dist_v = list(update_D[vertex].values())
                    self.rt_tbl_D[vertex] = {router: (dist_v[0] + dist_router)}
                    self.was_updated = True
                else:
                    dist_v = list(update_D[vertex].values())
                    dist_u = list(self.rt_tbl_D[vertex].values())
                    # Compare known cost to vertex with neighbor cost + cost to neighbor
                    if dist_u[0] > (dist_router + dist_v[0]):
                        self.rt_tbl_D[vertex] = (dist_router + dist_v[0])
                        self.was_updated = True

    # forward the packet according to the routing table
    # @param p Packet containing routing information
    def update_routes(self, p, i):
        route_update = json.loads(p.data_S[2:])
        router = p.data_S[0:2]
        self.bellman_ford(router, route_update)
        self.all_costs_D[router] = route_update
        print('%s: Received routing update %s from interface %d' % (self, p, i))
        if self.was_updated:
            self.all_costs_D[self.name] = self.rt_tbl_D
            self.send_routes(i)
            print('%s: Updated routes' % self)
        else:
            print('%s: No update Required' % self)

    # thread target for the host to keep forwarding data
    def run(self):
        print(threading.currentThread().getName() + ': Starting')
        while True:
            self.process_queues()
            if self.stop:
                print(threading.currentThread().getName() + ': Ending')
                return 