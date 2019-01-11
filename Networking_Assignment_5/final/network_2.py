import queue
import threading
from link_2 import LinkFrame
import json


## wrapper class for a queue of packets
class Interface:
    ## @param maxsize - the maximum size of the queue storing packets
    #  @param capacity - the capacity of the link in bps
    def __init__(self, maxsize=0, capacity=500):
        self.in_queue = queue.Queue(maxsize)
        self.out_queue = queue.Queue(maxsize)
        self.capacity = capacity #serialization rate
        self.next_avail_time = 0 #the next time the interface can transmit a packet
    
    ##get packet from the queue interface
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
        
    ##put the packet into the interface queue
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
            
## MPLSFrame class             
class MPLSFrame:

    mpls_label = 'M'
    mpls_label_length = len(mpls_label)

    def __init__(self, pkt_s):
        self.pkt_s = pkt_s

    ## called when printing the object
    def __str__(self):
        return self.to_byte_S()

    def to_byte_S(self):
        byte_S = str(self.mpls_label).zfill(self.mpls_label_length)
        byte_S += self.pkt_s
        return byte_S

    @classmethod
    def from_byte_S(self, mpls_frame_S):
        #pkt_s = mpls_frame_S[MPLSFrame.mpls_label_length : ].strip('0')
        pkt_s = mpls_frame_S[MPLSFrame.mpls_label_length : ]
        return pkt_s


## Implements a network layer packet
# NOTE: You will need to extend this class for the packet to include
# the fields necessary for the completion of this assignment.
class NetworkPacket:
    ## packet encoding lengths 
    dst_S_length = 5
    
    ##@param dst: address of the destination host
    # @param data_S: packet payload
    # @param priority: packet priority
    def __init__(self, dst, data_S, priority=0):
        self.dst = dst
        self.data_S = data_S
        #TODO: add priority to the packet class

        """print("\n\t\t*** PRIORITY PRINT ***\n\t\t*** PACKET: %s --- PRIORITY: %d ***\n" % (self, priority))"""
        
    ## called when printing the object
    def __str__(self):
        return self.to_byte_S()
        
    ## convert packet to a byte string for transmission over links
    def to_byte_S(self):
        byte_S = str(self.dst).zfill(self.dst_S_length)
        byte_S += self.data_S
        return byte_S
    
    ## extract a packet object from a byte string
    # @param byte_S: byte string representation of the packet
    @classmethod
    def from_byte_S(self, byte_S):
        dst = byte_S[0 : NetworkPacket.dst_S_length].strip('0')
        data_S = byte_S[NetworkPacket.dst_S_length : ]        
        return self(dst, data_S)
    

## Implements a network host for receiving and transmitting data
class Host:
    
    ##@param addr: address of this node represented as an integer
    def __init__(self, addr):
        self.addr = addr
        self.intf_L = [Interface()]
        self.stop = False #for thread termination
    
    ## called when printing the object
    def __str__(self):
        return self.addr
       
    ## create a packet and enqueue for transmission
    # @param dst: destination address for the packet
    # @param data_S: data being transmitted to the network layer
    # @param priority: packet priority
    def udt_send(self, dst, data_S, priority=0):
        pkt = NetworkPacket(dst, data_S)
        print('%s: sending packet "%s" with priority %d' % (self, pkt, priority))
        #encapsulate network packet in a link frame (usually would be done by the OS)
        fr = LinkFrame('Network', pkt.to_byte_S())
        #enque frame onto the interface for transmission
        self.intf_L[0].put(fr.to_byte_S(), 'out') 
        
    ## receive frame from the link layer
    def udt_receive(self):
        fr_S = self.intf_L[0].get('in')
        if fr_S is None:
            return
        #decapsulate the network packet
        fr = LinkFrame.from_byte_S(fr_S)
        assert(fr.type_S == 'Network') #should be receiving network packets by hosts
        pkt_S = fr.data_S
        print('%s: received packet "%s"' % (self, pkt_S))
       
    ## thread target for the host to keep receiving data
    def run(self):
        print (threading.currentThread().getName() + ': Starting')
        while True:
            #receive data arriving to the in interface
            self.udt_receive()
            #terminate
            if(self.stop):
                print (threading.currentThread().getName() + ': Ending')
                return
        


## Implements a multi-interface router
class Router:
    
    ##@param name: friendly router name for debugging
    # @param intf_capacity_L: capacities of outgoing interfaces in bps 
    # @param encap_tbl_D: table used to encapsulate network packets into MPLS frames
    # @param frwd_tbl_D: table used to forward MPLS frames
    # @param decap_tbl_D: table used to decapsulate network packets from MPLS frames
    # @param max_queue_size: max queue length (passed to Interface)
    def __init__(self, name, intf_capacity_L, encap_tbl_D, frwd_tbl_D, decap_tbl_D, max_queue_size):
        self.stop = False #for thread termination
        self.name = name

        #create a list of interfaces
        self.intf_L = [Interface(max_queue_size, intf_capacity_L[i]) for i in range(len(intf_capacity_L))]

        #save MPLS tables
        self.encap_tbl_D = encap_tbl_D
        self.frwd_tbl_D = frwd_tbl_D
        self.decap_tbl_D = decap_tbl_D

        # DEBUGGIN
        # ============================================================================================================== #
        print(
                '\n\t\t****> NODE [%s]: encapsulate table: %s <****\n'
                '\t\t****> NODE [%s]: forwarding table: %s <****\n'
                '\t\t****> NODE [%s]: dencapsulate table: %s <****\n'
                 % (
                     self.name, json.dumps(self.encap_tbl_D), 
                     self.name, json.dumps(self.frwd_tbl_D), 
                     self.name, json.dumps(self.decap_tbl_D)
                     ) 
             )   
        # ============================================================================================================== #      

    ## called when printing the object
    def __str__(self):
        return self.name

    ## look through the content of incoming interfaces and 
    # process data and control packets
    def process_queues(self):
        for i in range(len(self.intf_L)):
            fr_S = None #make sure we are starting the loop with a blank frame
            fr_S = self.intf_L[i].get('in') #get frame from interface i
            if fr_S is None:
                continue # no frame to process yet
            #decapsulate the packet
            fr = LinkFrame.from_byte_S(fr_S)
            pkt_S = fr.data_S

            #process the packet as network, or MPLS
            if fr.type_S == "Network":
                p = NetworkPacket.from_byte_S(pkt_S) #parse a packet out
                self.process_network_packet(p, i)
            elif fr.type_S == "MPLS":

                # TODO: handle MPLS frames
                # m_fr = MPLSFrame.from_byte_S(pkt_S) #parse a frame out
                #for now, we just relabel the packet as an MPLS frame without encapsulation

                # DEBUGGIN: DECAPSULATE MPLS
                # ===================================================================================================== #
                mplsFrame = MPLSFrame(pkt_S)
                mpls_frame_s = mplsFrame.from_byte_S(pkt_S)

                if mpls_frame_s[0] is 'M':
                    pkt_s = mpls_frame_s
                    mplsFrame = MPLSFrame(mpls_frame_s)
                    mpls_frame_s = mplsFrame.from_byte_S(pkt_s)

                print(
                        '\n\t\t @@@@=> DECAPSULATE MPLS --- PARSE A FRAME OUT <=@@@@\n'
                        '\t\t @@@@=> NODE [%s] --- got MPLS Frame: %s on INTF [%d] <=@@@@\n'
                        '\t\t @@@@=> NODE [%s] --- packet after decapsulation: %s <=@@@@\n'
                        % (
                            self.name,  pkt_S, i, self.name, mpls_frame_s
                          )
                     )
                # ===================================================================================================== #

                #m_fr = p
                m_fr = mplsFrame
                # m_fr = mpls_frame_s
                #send the MPLS frame for processing
                self.process_MPLS_frame(m_fr, i)
            else:
                raise('%s: unknown frame type: %s' % (self, fr.type))

    ## process a network packet incoming to this router
    #  @param p Packet to forward
    #  @param i Incoming interface number for packet p
    def process_network_packet(self, pkt, i):
        
        #TODO: encapsulate the packet in an MPLS frame based on self.encap_tbl_D
        #for now, we just relabel the packet as an MPLS frame without encapsulation

        # Check if we have to encapsulate packet into mpls
        # ===================================================================================================== #
        mplsFrame = None

        for key, value in self.encap_tbl_D.items():
             # RB and RC has negative values in encap_tbl_D, no need to incapsulate into mpls if its RB or RA
            if value > -1:
                if len(key) > 2:
                    """
                    print("\n\t\t========> NODE [%s] key: %s <========\n" % (self.name, key) )
                    print("\n\t\t========> key: %s --- key[ : 2]: %s <========\n" % (key, key[ : 2]) )
                    """
                    if self.name is 'RA':
                        # pkt_s = str(pkt)
                        pkt_s = pkt.to_byte_S()
                        mplsFrame = MPLSFrame(pkt_s)
                        mpls_frame = mplsFrame.to_byte_S()
                        print(
                                '\n\t\t!!!=> NODE [%s] --- IN INTERFACE: [%d] <=!!!\n'
                                '\t\t!!!=> NODE [%s]: ENCAPSULATE PACKET INTO MPLS <=!!!\n'
                                '\t\t!!!=> PACKET: %s ENCAPSULATED INTO MPLS: %s <=!!!\n'
                                % ( self.name, value, self.name, pkt_s, mpls_frame )
                            )
                else:
                    mplsFrame = pkt
                    print(
                            '\n\t\t>>>>> NODE [%s]: NO NEED TO ENCAPSULATE PACKET --- IN INTERFACE: %d <<<<<\n' 
                            '\n\t\t>>>>> NODE [%s]: PACKET: %s --- IN INTERFACE: %d <<<<<\n' 
                             % (self.name, i, self.name, mplsFrame, i) 
                         )
            else:
                mplsFrame = pkt
                print(
                        '\n\t\t>>>>> NODE [%s]: NO NEED TO ENCAPSULATE PACKET --- IN INTERFACE: %d <<<<<\n' 
                        '\n\t\t>>>>> NODE [%s]: PACKET: %s --- IN INTERFACE: %d <<<<<\n' 
                         % (self.name, i, self.name, mplsFrame, i) 
                      )
        # ===================================================================================================== #

        m_fr = mplsFrame
        # m_fr = pkt
        print('\n%s: encapsulated packet "%s" as MPLS frame "%s"\n' % (self, pkt, m_fr))
        #send the encapsulated packet for processing as MPLS frame
        self.process_MPLS_frame(m_fr, i)


    ## process an MPLS frame incoming to this router
    #  @param m_fr: MPLS frame to process
    #  @param i Incoming interface number for the frame
    def process_MPLS_frame(self, m_fr, i):

        #TODO: implement MPLS forward, or MPLS decapsulation if this is the last hop router for the path

        print('\nNODE [%s]: --- %s: processing MPLS frame "%s" from incoming interface "%d"\n' % (self.name, self, m_fr, i))
        # for now forward the frame out interface 1
        try:

            frame_flag = ''
            tmp_out_intf = -1

            pkt_s = ''
            mplsFrame = None
            mpls_frame_s = ''
            p = None

            # Loop via forward table
            # Loop via decapsulation table and cheack if frame have to be decapsulated
            for node_name, out_in_intf in self.frwd_tbl_D.items():

                    # Loop via decapsulation table and cheack if frame have to be decapsulated
                    for out_intf, next_hop_intf in out_in_intf.items():

                        # In this Network topology 'RD' is the last router, so MPLS frame have to be decapsulated,
                        # and Network Packet must be created to forward this packet into Host 3
                        if self.name is 'RD':
                            for decap_hop_name, decap_intf in self.decap_tbl_D.items(): 
                                if decap_intf == out_intf:
                                    frame_flag = 'Network'
                                    tmp_out_intf = out_intf

                                    # Decapsulate Frame
                                    pkt_s = str(m_fr)
                                    mplsFrame = MPLSFrame(pkt_s)
                                    mpls_frame_s = mplsFrame.from_byte_S(pkt_s)

                                    if mpls_frame_s[0] is 'M':
                                        pkt_s = mpls_frame_s
                                        mplsFrame = MPLSFrame(mpls_frame_s)
                                        mpls_frame_s = mplsFrame.from_byte_S(pkt_s)

                                    # Build Network Packet
                                    p = NetworkPacket.from_byte_S(mpls_frame_s)
                        elif self.name is 'RA':
                            frame_flag = 'MPLS'
                            tmp_out_intf = out_intf
                        else:
                            frame_flag = 'MPLS'
                            tmp_out_intf = out_intf

            # Forward Packets or Frames
            if frame_flag is 'Network':
                fr = LinkFrame('Network', p.to_byte_S())
                self.intf_L[out_intf].put(fr.to_byte_S(), 'out', True)
                print('@=> %s: forwarding frame "%s" from interface %d to %d <=@' % (self, fr, out_intf, i))
            elif frame_flag is 'MPLS':
                fr = LinkFrame('MPLS', m_fr.to_byte_S())
                self.intf_L[out_intf].put(fr.to_byte_S(), 'out', True)
                print('$=> %s: forwarding frame "%s" from interface %d to %d <=$' % (self, fr, out_intf, i))
            
        except queue.Full:
            print('%s: frame "%s" lost on interface %d' % (self, m_fr, i))
            pass
        
                
    ## thread target for the host to keep forwarding data
    def run(self):
        print (threading.currentThread().getName() + ': Starting')
        while True:
            self.process_queues()
            if self.stop:
                print (threading.currentThread().getName() + ': Ending')
                return 