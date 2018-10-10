#########################################################################################################################
#                                       [This sources was extremely helpful]                                            #
# Sources: [https://www.youtube.com/watch?v=2FwNy4Gxyh4&feature=youtu.be&list=PLfsQAZ9-6TC3yQmKmEphTsmuZCTkzyPI3]       #
#          [https://www.youtube.com/watch?v=CG5-slb_mWY&feature=youtu.be]                                               #
#          [https://stackoverflow.com/questions/40867447/python-simple-http-server-not-loading-font-awesome-fonts]      #
#          [https://en.wikipedia.org/wiki/Media_type]                                                                   #
#########################################################################################################################

#######################################################
# University: Montana Satate University               #
# Class: CSCI 466                                     #
# Project Name: PA1 - Battleship Network Application  #
# Author: Olexandr Matveyev, Cas Loftin               #
#                                                     #
# If you have to use some of my files from            #
# my GitHub repository, please let me know.           #
#######################################################

# client B
#import http.client
import requests
import sys

# GLOBAL
conn = None

server_ip = ''
server_port = 0


# CONNECTION
# ====================================================================

def start(x, y):

    # Just request string
    request_str = "/?x=%s&y=%s" % (x, y)

    # Connect to a server and send a request
    req = requests.get("http://%s:%d%s" % (server_ip, server_port, request_str) )
    print(req.text)
    

    """
    req = requests.get("http://%s:%d%s" % (server_ip, server_port, "/result") )
    print("\n%s" % (req.text) ) # print server response
    """
    
    return

# ====================================================================


if __name__ == "__main__":

    # READ: arguments
    ip = str(sys.argv[1])
    port = int(sys.argv[2])

    x = sys.argv[3]
    y = sys.argv[4]

    server_ip = ip
    server_port = port

    start(x, y)