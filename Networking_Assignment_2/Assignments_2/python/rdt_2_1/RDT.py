import Network
import argparse
from time import sleep
import hashlib


class Packet:
    ## the number of bytes used to store packet length
    seq_num_S_length = 10
    length_S_length = 10

    ## length of md5 checksum in hex
    checksum_length = 32 
        
    def __init__(self, seq_num, msg_S):
        self.seq_num = seq_num
        self.msg_S = msg_S
    
    # Packet should handle ACK and NAK flags
    # basically init method should be changed

    @classmethod
    def from_byte_S(self, byte_S):
        if Packet.corrupt(byte_S):
            raise RuntimeError('Cannot initialize Packet: byte_S is corrupt')

        #extract the fields
        # slice the byte_S[ 0: (10 + sequence number) ]
        seq_num = int(byte_S[Packet.length_S_length : Packet.length_S_length + Packet.seq_num_S_length])

        # slice the byte_S[ (10 + sequence number + checksum_length) : last index ]
        msg_S = byte_S[Packet.length_S_length + Packet.seq_num_S_length + Packet.checksum_length :]

        #[TEST]
        print("\n=====================================")
        print("Packet: from_byte_S(self, byte_S):")
        print("\tseq_num: %s" % (seq_num) )
        print("\tmsg_S: IT IS JUST Client STRING")
        print("\tbyte_S: %s" % (byte_S) )
        print("=====================================\n")

        return self(seq_num, msg_S)
        
        
    def get_byte_S(self):
        #convert sequence number of a byte field of seq_num_S_length bytes
        seq_num_S = str(self.seq_num).zfill(self.seq_num_S_length)
        
        # Note
        # ============================================================= #
        # The method zfill() pads string on the left with zeros to fill width.
        # width - width of the string
        #length_S = str().zfill(width); 

        # TEST
        demo_length = 4
        demo_str = ''.zfill(demo_length)
        # out-put is 0000
        # ============================================================= #

        # The packet length: convert length to a byte field of length_S_length bytes
        packet_length = self.length_S_length + len(seq_num_S) + self.checksum_length + len(self.msg_S)

        # fill in the byte field with the packet_length
        length_S = str(packet_length).zfill(self.length_S_length)
        
        #compute the checksum
        checksum = hashlib.md5((length_S + seq_num_S + self.msg_S).encode('utf-8'))
        checksum_S = checksum.hexdigest()
        
        #[TEST]
        print("\n=====================================")
        print("Packet: get_byte_S(self):")
        print("\tpacket_length: %d" % (packet_length) )
        print("\tseq_num_S: " + seq_num_S)
        print("\tlength_S: " + length_S)
        print("\tchecksum_S: " + checksum_S)
        print("\tmsg_S: " + self.msg_S)
        print("=====================================\n")

        #compile into a string
        return length_S + seq_num_S + checksum_S + self.msg_S
   
    
    @staticmethod
    def corrupt(byte_S):

        # Note
        # =================================================================================== #
        # Slicing an Array: Python has a slicing feature which allows to access pieces of an array. We, basically,
        # slice an array using a given range (eg. X to Y position [including X and Y] ), giving us elements we require. 
        # This is done by using indexes separated by a colon [x : y]
        # 
        #
        # The UDP package:
        # A: UDP Header [8 Bytes --- 64 Bits]:
        #    1: Source port number -------> 2 bytes 0:7 bits
        #    2: Destination port number --> 2 bytes 8:15 bits
        #    3: Length -------------------> 2 bytes 16:23 bits
        #    4: Checksum -----------------> 2 bytes 24:31 bits
        # B: UDP Body [24 Bytes --- 192 Bits]:
        #    1: Payload Data (if any), app data, message
        # =================================================================================== #


        #extract the fields
        # [0:10]
        length_S = byte_S[0:Packet.length_S_length]

        # [10:20]
        seq_num_S = byte_S[Packet.length_S_length : Packet.seq_num_S_length + Packet.seq_num_S_length]
        
        # [20:20 + checksum_length "hex"]
        checksum_S = byte_S[Packet.seq_num_S_length + Packet.seq_num_S_length : Packet.seq_num_S_length + Packet.length_S_length + Packet.checksum_length]
        
        # [20 + checksum_length "hex": last index]
        msg_S = byte_S[Packet.seq_num_S_length + Packet.seq_num_S_length + Packet.checksum_length :]
        
        #compute the checksum locally
        checksum = hashlib.md5(str(length_S+seq_num_S+msg_S).encode('utf-8'))
        computed_checksum_S = checksum.hexdigest()

        #[TEST]
        print("\n=====================================")
        print("Packet: corrupt(byte_S):")
        print("\tlength_S: " + length_S)
        print("\tseq_num_S: " + seq_num_S)
        print("\tchecksum_S: " + checksum_S)
        print("\tmsg_S: " + msg_S)
        print("\tchecksum_length: %d" % (Packet.checksum_length) )
        print("\tcomputed_checksum_S: " + computed_checksum_S)
        print("=====================================\n")

        #and check if the same
        return checksum_S != computed_checksum_S

    def ack(self, ack_flag, checksum):

        # build acknowledgment packet

        pass

    def nak(self, nak_flag, checksum):

        # build negative acknowledgement

        pass
        

class RDT:
    ## latest sequence number used in a packet
    seq_num = 1

    ## buffer of bytes read from network
    byte_buffer = '' 

    def __init__(self, role_S, server_S, port):
        self.network = Network.NetworkLayer(role_S, server_S, port)
    
    def disconnect(self):
        self.network.disconnect()
        
    def rdt_1_0_send(self, msg_S):
        p = Packet(self.seq_num, msg_S)
        self.seq_num += 1
        self.network.udt_send(p.get_byte_S())
        
    def rdt_1_0_receive(self):
        ret_S = None
        byte_S = self.network.udt_receive()
        self.byte_buffer += byte_S

        #keep extracting packets - if reordered, could get more than one
        while True:
            #check if we have received enough bytes
            if(len(self.byte_buffer) < Packet.length_S_length):
                #not enough bytes to read packet length
                return ret_S 
            
            #extract length of packet
            length = int(self.byte_buffer[:Packet.length_S_length])
            
            print("\n=====================================")
            print("RDT: rdt_1_0_receive")
            print("\tlength: %d" % (length) )
            print("=====================================\n")

            if len(self.byte_buffer) < length:
                #not enough bytes to read the whole packet
                return ret_S 
            
            #create packet from buffer content and add to return string
            p = Packet.from_byte_S(self.byte_buffer[0:length])
            ret_S = p.msg_S if (ret_S is None) else ret_S + p.msg_S

            #remove the packet bytes from the buffer
            self.byte_buffer = self.byte_buffer[length:]
            #if this was the last packet, will return on the next iteration
            
    
    def rdt_2_1_send(self, msg_S):

        # [Notes]
        # =========================================================================================================== #
        # Note source: https://astro.temple.edu/~stafford/cis320f05/lecture/chap3/deluxe-content.html

        # Using: positive acknowledgments ("OK") and negative acknowledgments ("Please repeat that."). 
        # These control messages allow the receiver to let the sender know what has been received correctly, 
        # and what has been received in error and thus requires repeating.
        # In a computer network setting, reliable data transfer protocols based on such re-transmission 
        # are known ARQ (Automatic Repeat reQuest) protocols. 

        # Three additional protocol capabilities are required in ARQ
        # 1: Error detection
        # 2: Receiver feedback
        # 3: Re-transmission
        # *: known as Stop-and-Wait protocols
        # 
        # But we also have to handle corrupted ACKs or NAKs
        # =========================================================================================================== #

        # 1: Make Packet: sequence number, message, checksum
        # 2: Send Packet
        # 3: wait for acknowledgments
        # 4: if ACK: send next packet
        # 5: if NAK: re-sent previous packet

        pass
        
    def rdt_2_1_receive(self):

        # 1: receive packet
        # 2: retrieve data from the packet: sequence number, message, checksum
        # 3: verify checksum
        # 4: if checksum IS OK: sent ACK
        # 5: if checksum IS NOT OK: sent NAK


        pass
    
    def rdt_3_0_send(self, msg_S):
        pass
        
    def rdt_3_0_receive(self):
        pass
        

if __name__ == '__main__':
    parser =  argparse.ArgumentParser(description='RDT implementation.')
    parser.add_argument('role', help='Role is either client or server.', choices=['client', 'server'])
    parser.add_argument('server', help='Server.')
    parser.add_argument('port', help='Port.', type=int)
    args = parser.parse_args()
    
    rdt = RDT(args.role, args.server, args.port)
    if args.role == 'client':
        rdt.rdt_1_0_send('MSG_FROM_CLIENT')
        sleep(2)
        print(rdt.rdt_1_0_receive())
        rdt.disconnect()
        
        
    else:
        sleep(1)
        print(rdt.rdt_1_0_receive())
        rdt.rdt_1_0_send('MSG_FROM_SERVER')
        rdt.disconnect()
        


        
        