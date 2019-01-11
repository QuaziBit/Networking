'''
Created on Oct 12, 2016

@author: mwittie
'''
import network_2
import link_2
import threading
from time import sleep

##configuration parameters
router_queue_size = 0 #0 means unlimited
simulation_time = 1 #give the network sufficient time to transfer all packets before quitting
mtu_length = 40
mtu_length_2 = 25
dst_addr_S_length = 5



# Build segment
# returns dictionary, where key is segment number and value is segment string
def buildSegment(packet, mtu_length): 

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


if __name__ == '__main__':
    object_L = [] #keeps track of objects, so we can kill their threads
    
    #create network nodes
    client = network_2.Host(1)
    object_L.append(client)
    server = network_2.Host(2)
    object_L.append(server)
    router_a = network_2.Router(name='A', intf_count=1, max_queue_size=router_queue_size)
    object_L.append(router_a)
    
    #create a Link Layer to keep track of links between network nodes
    link_layer = link_2.LinkLayer()
    object_L.append(link_layer)
    
    #add all the links
    #link parameters: from_node, from_intf_num, to_node, to_intf_num, mtu/mtu_length
    
    # Link between client and a router
    link_layer.add_link(link_2.Link(client, 0, router_a, 0, mtu_length))
    
    # Link between router and a client 
    link_layer.add_link(link_2.Link(router_a, 0, server, 0, mtu_length_2))
    
    
    #start all the objects
    thread_L = []
    thread_L.append(threading.Thread(name=client.__str__(), target=client.run))
    thread_L.append(threading.Thread(name=server.__str__(), target=server.run))
    thread_L.append(threading.Thread(name=router_a.__str__(), target=router_a.run))
    
    thread_L.append(threading.Thread(name="Network", target=link_layer.run))
    
    for t in thread_L:
        t.start()
        
    #create some send events   
    # ==================================================================================================== #
    
    #create some send events    
    for i in range(3):

        # Length: 103
        data = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBCCCCCCCCCCCCCCCCCCCCC"

        # splitting-up packet
        segments = buildSegment(data, mtu_length)
        for key, segment in segments.items():
            #print("KEY: %d --- data: %s\n" % (key, segment) )
            client.udt_send(2, '%s %d' % (segment, i) )
    
    # ==================================================================================================== #
    
    #give the network sufficient time to transfer all packets before quitting
    sleep(simulation_time)
    
    #join all threads
    for o in object_L:
        o.stop = True
    for t in thread_L:
        t.join()
        
    print("All simulation threads joined")



# writes to host periodically