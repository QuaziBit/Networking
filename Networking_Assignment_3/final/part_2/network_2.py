'''
Created on Oct 12, 2016

@author: mwittie
'''
import queue
import threading
import textwrap


## wrapper class for a queue of packets
class Interface:
    ## @param maxsize - the maximum size of the queue storing packets
    def __init__(self, maxsize=0):
        self.queue = queue.Queue(maxsize)
        self.mtu = None
    
    ##get packet from the queue interface
    def get(self):
        try:
            return self.queue.get(False)
        except queue.Empty:
            return None
        
    ##put the packet into the interface queue
    # @param pkt - Packet to be inserted into the queue
    # @param block - if True, block until room in queue, if False may throw queue.Full exception
    def put(self, pkt, block=False):
        self.queue.put(pkt, block)
        
        
## Implements a network layer packet (different from the RDT packet 
# from programming assignment 2).
# NOTE: This class will need to be extended to for the packet to include
# the fields necessary for the completion of this assignment.
class NetworkPacket:
    # packet encoding lengths
    dst_addr_S_length = 5
    flag_S_length = 1
    offset_S_length = 2
    header_length = dst_addr_S_length + flag_S_length + offset_S_length

    # @param dst_addr: address of the destination host
    # @param data_S: packet payload
    def __init__(self, dst_addr, data_S, flag=0, offset=0):
        self.dst_addr = dst_addr
        self.data_S = data_S
        self.flag = flag
        self.offset = offset

    # called when printing the object
    def __str__(self):
        return self.to_byte_S()

    # convert packet to a byte string for transmission over links
    def to_byte_S(self):
        if self.flag == 1:
            byte_S = str(self.dst_addr).zfill(self.dst_addr_S_length)
            byte_S += str(self.flag).zfill(self.flag_S_length)
            byte_S += str(self.offset).zfill(self.offset_S_length)
            byte_S += self.data_S
        else:
            byte_S = str(self.dst_addr).zfill(self.dst_addr_S_length)
            byte_S += self.data_S
        return byte_S

    @classmethod
    def is_frag(self, byte_S):
        if byte_S[self.flag_S_length] is '1':
            return True
        return False

    # extract a packet object from a byte string
    # @param byte_S: byte string representation of the packet
    @classmethod
    def from_byte_S(self, byte_S, mtu):
        packets = []
        dst_addr = int(byte_S[0: NetworkPacket.dst_addr_S_length])
        data_S = byte_S[NetworkPacket.dst_addr_S_length:]

        # Fragment
        offset_size = 0
        while True:
            self.flag = 1 if self.header_length + len(data_S[offset_size:]) > mtu else 0
            packets.append(self(dst_addr, data_S[offset_size:offset_size + mtu - self.header_length], self.flag, offset_size))
            offset_size = offset_size + mtu - self.header_length
            if len(data_S[offset_size:]) == 0:
                break
        return packets


# Implements a network host for receiving and transmitting data
class Host:
    # @param addr: address of this node represented as an integer
    def __init__(self, addr):
        self.addr = addr
        self.in_intf_L = [Interface()]
        self.out_intf_L = [Interface()]
        self.stop = False  # for thread termination

    # called when printing the object
    def __str__(self):
        return 'Host_%s' % self.addr



    # Build segment
    # returns dictionary, where key is segment number and value is segment string
    def buildSegment(self): 

        packet = self.packet
        mtu_length = self.mtu_length

        # packet encoding lengths 
        # this variable defined in the network.py
        dst_addr_S_length = 5
                    
        # packet-data length
        data_length = len(packet)
            
        # SPLITING-UP PACKET INTO SMALLER SEGMENTS: MAX SEGMENT LENGTH: mtu_length
        # SMALL PIECE OF PACKET/SEGMENT: String
        segment = ""

        # Dictionary to store all segments of current packet
        segments = dict()

        # SEGMENT NUMBER
        # it is key of the dictionary
        i = 1

        # START-RANGE: TO SPLIT UP PACKET
        start_index = 0

        # WE HAVE TO RESERVE SOME SPACE IN OUR SEGMENT FOR THE [destination address] and [port],
        # SO THE FINAL LENGTH OF THE SEGMENT SHOULD BE NO MORE THAN [mtu_length - (dst_addr_S_length * 2)],
        # were st_addr_S_length * 2 is just (dst_addr_S_length + port)
        # (dst_addr_S_length * 2): JUST TO MAKE SURE THAT WE GOT ENOUGH SPACE TO INCLUDE ALL HEADERS
        end_index = mtu_length - (dst_addr_S_length * 2)

        # Infinite loop 
        # it will stopped after all packet will segmented
        while True:

            # PULLING-UP DATA STRINGS IN THE RANGE [start_index --- end_index]
            segment = packet[start_index : end_index]
                        
            # IF 0 DATA LEFT: break loop
            if len(segment) == 0:
                break
                        
            # DEBUGGING INFO
            #print("\tSEGMENT [%d] length: %d --- SEGMENT DATA: %s" % ((i), len(segment), segment) )
                        
            # CHANGING THE RANGE OF start_index AND end_index
            # ============================================================================ #
            start_index = end_index
                        
            left = data_length - start_index
            if left > mtu_length:
                end_index += start_index
            else:
                end_index = data_length

            segments[i] = segment

            # SEGMENT NUMBER
            i += 1
            # ============================================================================ #

        # return dictionary of segments
        return segments




    # create a packet and enqueue for transmission
    # @param dst_addr: destination address for the packet
    # @param data_S: data being transmitted to the network layer
    def udt_send(self, dst_addr, data_S):
        self.mtu_out = self.out_intf_L[0].mtu
        #print("\t\t\t***udt_send IN %s****\n" % (self) )
        #print("\t\t\t***udt_send packet length: %d --- mtu out length: %d" % ( len(data_S), self.mtu_out ) )

        # TEST
        # Check if packet is to large, if yes split it into segments
        # ==================================================================================================== #
        # IMPORTANT:
        #   When we got packet from the host, such packet has [ADDRESS DATA]
        #   After we build a segment, this new segment should include an address, each segment of the packet
        #   should have an address. Be carful when splitting-up packet

        # Dictionary to store all segments of current packet
        segments = dict()

        #mtu = self.mtu_out
        mtu = 30

        # TEST
        pkt_S = data_S
        if pkt_S != None:
            if len(pkt_S) > mtu:
                print("\n\t***FROM %s: packet is to large --- mtu: %d --- packet: %d***\n\n" % (self, self.out_intf_L[0].mtu, len(pkt_S)) )
                #print("\n\t***FROM %s: packet: %s***\n\n" % (pkt_S) )

                print("SPLITTING-UP PACKET: IN %s\n" % (self) )

                # pull-out destination address from the received packet
                #dst_addr = int(pkt_S[0 : NetworkPacket.dst_addr_S_length])
                        
                # pull-out data from the received packet
                # we have to split this data into segments
                # store it in the self
                self.packet = pkt_S[NetworkPacket.dst_addr_S_length : ]
                        
                # store mtu length it in the self
                self.mtu_length = mtu
                        
                # build segments
                segments = self.buildSegment()

                # print segments
                print("PACKET ADDRESS: %d" % (dst_addr) )
                for key, segment in segments.items():
                    print("\t\t%s --- KEY: %d --- data: %s\n" % (self, key, segment) )
            # ==================================================================================================== #

        for key, segment in segments.items():
            p = NetworkPacket(dst_addr, segment)
            self.out_intf_L[0].put(p.to_byte_S()) #send packets always enqueued successfully
            print('\n%s: sending packet "%s" on the out interface with mtu=%d' % (self, p, self.out_intf_L[0].mtu))



    # receive packet from the network layer
    frag_buffer = []

    def udt_receive(self):
        self.mtu_in = self.in_intf_L[0].mtu
        #print("\t\t\t***udt_receive IN %s****\n" % (self) )

        """
        if (self.mtu_in is not None) and (self.in_intf_L[0].get() is not None):
            print("\t\t\t***udt_receive packet length: %d --- mtu in length: %d" % ( len(self.in_intf_L[0].get()), self.mtu_in  ) )
        """
            

        pkt_S = self.in_intf_L[0].get()
        if pkt_S is not None:
            self.frag_buffer.append(pkt_S[NetworkPacket.header_length:])
            if not NetworkPacket.is_frag(pkt_S):
                print('%s: received packet "%s"' % (self, ''.join(self.frag_buffer)))
                self.frag_buffer.clear()

    # thread target for the host to keep receiving data
    def run(self):
        print(threading.currentThread().getName() + ': Starting')
        while True:
            # receive data arriving to the in interface
            self.udt_receive()
            # terminate
            if self.stop:
                print(threading.currentThread().getName() + ': Ending')
                return


# Implements a multi-interface router described in class
class Router:
    # @param name: friendly router name for debugging
    # @param intf_count: the number of input and output interfaces
    # @param max_queue_size: max queue length (passed to Interface)
    def __init__(self, name, intf_count, max_queue_size):
        self.stop = False  # for thread termination
        self.name = name
        # create a list of interfaces
        self.in_intf_L = [Interface(max_queue_size) for _ in range(intf_count)]
        self.out_intf_L = [Interface(max_queue_size) for _ in range(intf_count)]

    # called when printing the object
    def __str__(self):
        return 'Router_%s' % self.name


    # look through the content of incoming interfaces and forward to
    # appropriate outgoing interfaces
    def forward(self):
        
        mtu = 30 # it should be set in the simulation

        for i in range(len(self.in_intf_L)):
            pkt_S = None
            try:
                # get packet from interface i
                pkt_S = self.in_intf_L[i].get()


                # if packet exists make a forwarding decision
                if pkt_S is not None:
                    # parse a packet out
                    packets = NetworkPacket.from_byte_S(pkt_S, mtu)


                    print("\t\t\t***forward packet: %s***" % (pkt_S) )


                    # HERE you will need to implement a lookup into the
                    # forwarding table to find the appropriate outgoing interface
                    # for now we assume the outgoing interface is also i


                    for p in packets:
                        self.out_intf_L[i].put(p.to_byte_S(), True)
                        print(
                            '%s: forwarding packet "%s" from interface %d to %d' % (self, p.to_byte_S(), i, i))
            except queue.Full:
                print('%s: packet "%s" lost on interface %d' % (self, p, i))
                pass

    # thread target for the host to keep forwarding data
    def run(self):
        print(threading.currentThread().getName() + ': Starting')
        while True:
            self.forward()
            if self.stop:
                print(threading.currentThread().getName() + ': Ending')
                return
