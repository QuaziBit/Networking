from network_3 import Router, Host
from link_3 import Link, LinkLayer
import threading
from time import sleep
import sys
from copy import deepcopy

##configuration parameters
router_queue_size = 0 #0 means unlimited
simulation_time = 15 #give the network sufficient time to execute transfers

if __name__ == '__main__':
    object_L = [] #keeps track of objects, so we can kill their threads at the end
    
    #create network hosts
    host_1 = Host('H1')
    object_L.append(host_1)
    host_2 = Host('H2')
    object_L.append(host_2)
    host_3 = Host('H3')
    object_L.append(host_3)
    
    # NOTES
    # ================================================================================================================== #
    # encap_tbl_D = {'NODE-NAME': N} where  
    # NODE-NAME: IS JUST A NODE NAME THAT WILL ACCEPT INCOMING PACKET
    # N: INPUT INTERFACE NUMBER

    # decap_tbl_D = {'NODE-NAME': N} where 
    # NODE-NAME: IS JUST A NODE NAME
    # N: OUTPUT INTERFACE NUMBER, SO MPLS FRAME MUST BE DECAMPSOLATED BEFORE SENDING IT VIA THIS INTERFACE

    # frwd_tbl_D = {'NAME-A': {X, Y}, 'NAME-B': {E, D}} WHERE
    # NAME-A AND NAME-B ARE TWO NODES CONNECTED TO EACH OTHER DIRECTLY 
    # X: OUTPUT-INTERFACE OF CARRENT NODE , Y: INPUT INTERFACE FOR NEXT NODE "NAME-B" IT IS INTERFACE OF ANOTHER NODE
    # E: OUTPUT-INTERFACE OF CARRENT NODE, D: INPUT INTERFACE FOR NEXT NODE "NAME-B" IT IS INTERFACE OF ANOTHER NODE
    # ================================================================================================================== #

    # @@@@=> IMPORTANT: THE FLOW OF PACKETS IN THIS TOPOLOGY IS FROM H1 AND H2 TO H3 <=@@@@

    #create routers and routing tables for connected clients (subnets)
    # ROUTER A "1"
    encap_tbl_D = {'RA-1': 0, 'RA-2': 1}    # table used to encapsulate network packets into MPLS frames
    frwd_tbl_D = {'RA-1': {2: 0}, 'RA-2': {3: 0}}     # table used to forward MPLS frames
    decap_tbl_D = {'RA-1': 2, 'RA-2': 3}    # table used to decapsulate network packets from MPLS frames
    router_a = Router(name='RA', 
                              intf_capacity_L=[500,500,500,500],
                              encap_tbl_D = encap_tbl_D,
                              frwd_tbl_D = frwd_tbl_D,
                              decap_tbl_D = decap_tbl_D, 
                              max_queue_size=router_queue_size)
    object_L.append(router_a)

    # ROUTER B "2"
    encap_tbl_D = {'RB': -1} # -1 because no encapsulation in this topology needed for MPLS
    frwd_tbl_D = {'RB': {1: 0}}
    decap_tbl_D = {'RB': -1} # -1 because no decapsulation in this topology needed for MPLS
    router_b = Router(name='RB', 
                              intf_capacity_L=[500,500],
                              encap_tbl_D = encap_tbl_D,
                              frwd_tbl_D = frwd_tbl_D,
                              decap_tbl_D = decap_tbl_D, 
                              max_queue_size=router_queue_size)
    object_L.append(router_b)

    # ROUTER C "3"
    encap_tbl_D = {'RC': -1} # -1 because no encapsulation in this topology needed for MPLS
    frwd_tbl_D = {'RC': {1: 1}}
    decap_tbl_D = {'RC': -1} # -1 because no decapsulation in this topology needed for MPLS
    router_c = Router(name='RC', 
                              intf_capacity_L=[500,500],
                              encap_tbl_D = encap_tbl_D,
                              frwd_tbl_D = frwd_tbl_D,
                              decap_tbl_D = decap_tbl_D, 
                              max_queue_size=router_queue_size)
    object_L.append(router_c)

    # ROUTER D "4"
    encap_tbl_D = {'RD-1': 0, 'RD-2': 1} # -1 because no encapsulation in this topology needed for MPLS
    frwd_tbl_D = {'RD': {2: 0}}
    decap_tbl_D = {'RD': 2} # -1 because no decapsulation in this topology needed for MPLS
    router_d = Router(name='RD', 
                              intf_capacity_L=[500,500,500],
                              encap_tbl_D = encap_tbl_D,
                              frwd_tbl_D = frwd_tbl_D,
                              decap_tbl_D = decap_tbl_D, 
                              max_queue_size=router_queue_size)
    object_L.append(router_d)
    
    #create a Link Layer to keep track of links between network nodes
    link_layer = LinkLayer()
    object_L.append(link_layer)
    
    #add all the links - need to reflect the connectivity in cost_D tables above
    link_layer.add_link(Link(host_1, 0, router_a, 0))
    link_layer.add_link(Link(host_2, 0, router_a, 1))

    link_layer.add_link(Link(router_a, 2, router_b, 0))
    link_layer.add_link(Link(router_a, 3, router_c, 0))
    link_layer.add_link(Link(router_b, 1, router_d, 0))
    link_layer.add_link(Link(router_c, 1, router_d, 1))

    link_layer.add_link(Link(router_d, 2, host_3, 0))
    
    
    #start all the objects
    thread_L = []
    for obj in object_L:
        thread_L.append(threading.Thread(name=obj.__str__(), target=obj.run)) 
    
    for t in thread_L:
        t.start()
    
    #create some send events    
    for i in range(5):
        priority = i%2
        """
        tmp_msg = '%dMESSAGE_%d_FROM_H1' % (priority, i)
        host_1.udt_send('H1', tmp_msg, priority )
        """
        print(
                '\n\t\t\t\t $#####=> IN SIMULATION --- packet: %s priority: %d <=#####$\n' 
                 % ( ('MESSAGE_%d_FROM_H1' % i) , priority) 
             )

        host_1.udt_send('H3', 'MESSAGE_%d_FROM_H1' % i, priority)
        # host_1.udt_send('H2', 'MESSAGE_%d_FROM_H2' % i, priority)
        
    #give the network sufficient time to transfer all packets before quitting
    sleep(simulation_time)

    
    #join all threads
    for o in object_L:
        o.stop = True
    for t in thread_L:
        t.join()
        
    print("All simulation threads joined")