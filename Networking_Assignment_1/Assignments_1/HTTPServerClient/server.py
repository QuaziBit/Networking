#########################################################################################################################
#                                       [This sources was extremely helpful]                                            #
# Sources: [https://www.youtube.com/watch?v=2FwNy4Gxyh4&feature=youtu.be&list=PLfsQAZ9-6TC3yQmKmEphTsmuZCTkzyPI3]       #
#          [https://www.youtube.com/watch?v=CG5-slb_mWY&feature=youtu.be]                                               #
#          [https://stackoverflow.com/questions/40867447/python-simple-http-server-not-loading-font-awesome-fonts]      #
#########################################################################################################################

#######################################################
# University: Montana Satate University               #
# Class: CSCI 466                                     #
# Project Name: PA1 - Battleship Network Application  #
# Author: Olexandr Matveyev                           #
#                                                     #
# If you have to use some of my files from            #
# my GitHub repository, please let me know.           #
#######################################################

# server B
from http.server import BaseHTTPRequestHandler, HTTPServer
import re
import cgi
import sys
import os

# Global
# =======================================================================
server_ip = '127.0.0.1'
port = 0
ownFileName = ""
opponentFileName = ""
board = ""
user_x = 0
user_y = 0

# Game board size
board_size = 10

# 2D List to store own board
ownBoard = [[0] * board_size for i in range(board_size)]
ownPoints = 0

# 2D List to store opponent board
opponentBoard = [[0] * board_size for i in range(board_size)]
opponentPoints = 0

# store absolute path of the current directory
#homeFolderPath = ""
# =======================================================================

class httpServerHandler(BaseHTTPRequestHandler):
    
    # HTTP DO_GET
    def do_GET(self):

        # Handle HTTP GET Requests
        try:

            # Try to load CSS and jQuery
            # =========================================================================================
            if self.path.endswith("/css/own_board.css"):

                self.send_response(200)
                self.send_header('Content-type', 'text/css')
                self.end_headers()

                # Get absolute path to the css file
                scriptPath = os.path.realpath(__file__)
                homeFolderPath = os.path.dirname(scriptPath)
                cssPath = "%s\css\own_board.css" % (homeFolderPath)

                """
                print("CSS file path: %s\css\own_board.css\n" % (homeFolderPath) )
                print(curdir + sep + self.path)
                """
                
                # Read css file
                tmpFile = open(cssPath, 'rb')

                # Send to the server content of js file
                self.wfile.write( tmpFile.read() )

                # Stop reading file
                tmpFile.close()

                return

            if self.path.endswith("/js/jquery_2_2_4_min.js"):

                self.send_response(200)
                self.send_header('Content-type', 'application/javascript')
                self.end_headers()

                # Get absolute path to the js file
                scriptPath = os.path.realpath(__file__)
                homeFolderPath = os.path.dirname(scriptPath)
                jsPath = "%s\js\jquery_2_2_4_min.js" % (homeFolderPath)

                """
                print("JS file path: %s\js\jquery_2_2_4_min.js\n" % (homeFolderPath) )
                print(curdir + sep + self.path)
                """
                
                # Read js file
                tmpFile = open(jsPath, 'rb')

                # Send to the server content of js file
                self.wfile.write( tmpFile.read() )

                # Stop reading file
                tmpFile.close()

                return

            if self.path.endswith("/js/own_board.js"):

                self.send_response(200)
                self.send_header('Content-type', 'application/javascript')
                self.end_headers()

                # Get absolute path to the js file
                scriptPath = os.path.realpath(__file__)
                homeFolderPath = os.path.dirname(scriptPath)
                jsPath = "%s\js\own_board.js" % (homeFolderPath)

                """
                print("JS file path: %s\js\own_board.js\n" % (homeFolderPath) )
                print(curdir + sep + self.path)
                """
                
                # Read js file
                tmpFile = open(jsPath, 'rb')

                # Send to the server content of js file
                self.wfile.write( tmpFile.read() )

                # Stop reading file
                tmpFile.close()

                return

            # Handle application requests
            # such as:
            # 1: http://server:server-port/opponent_board.html
            # 2: http://server:server-port/own_board.html
            # 3: http://server:server-port/?x=n&y=n
            # =========================================================================================
            if self.path.endswith("/opponent_board.html"): # http://127.0.0.1:5000/opponent_board.html

                # This url should be accessed via web-brauser
                # url: http://127.0.0.1:5000/opponent_board.html
                # or url: http://server:server-port/opponent_board.html

                # set response key
                self.send_response(200)

                # build header
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                # get board in the html format
                # should be displayed in the web-browser
                html = showOpponentBoard()

                # send responce and html to the client
                self.wfile.write( bytes(html, "utf-8") )

                # Print to console
                print("\nHEADER-INFORMATION")
                print("======================================================")
                print("%s" % (self.headers) )

                return
            elif self.path.endswith("/own_board.html"): # http://127.0.0.1:5000/own_board.html
                
                # This url should be accessed via web-brauser
                # url: http://127.0.0.1:5000/own_board.html
                # or url: http://server:server-port/own_board.html

                # set response key
                self.send_response(200)

                # build header
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                # get board in the html format
                # should be displayed in the web-browser
                html = showOwnBoard()

                # send responce and html to the client
                self.wfile.write( bytes(html, "utf-8") )
                
                # Print to console
                print("\nHEADER-INFORMATION")
                print("======================================================")
                print("%s" % (self.headers) )

                return
            elif self.path.endswith("/result"): # http://127.0.0.1:500/result

                # This url should be accessed via web-brauser
                # url: http://127.0.0.1:5000/result
                # or url: http://server:server-port/result
                # or it can be accessed via client.py

                # set response key
                self.send_response(200)

                # build header
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                reply = "HTTP Request\nURL: %s%d%s\n%s" % (server_ip, port, self.path, self.headers )

                # get board in the html format
                self.wfile.write( bytes(reply, "utf-8") )

                # Print to console
                print("======================================================")
                print("%s" % (self.headers) )

                return
            else:

                # This url should be accessed via web-brauser
                # url: http://127.0.0.1:5000/?x=n&y=n
                # or url: http://server:server-port/?x=n&y=n
                # or it can be accessed via client.py

                # Retriving values from the url
                # ==========================================================================
                # parsURL should return two digits
                values = parsURL(self.path)
                x = values[0]
                y = values[1]
                x_bounderis = False
                y_bounderis = False
                formatted = True
                # ========================================

                # if x and y in the range 0 to 9 then OK Request
                # if x or y in the range -inf to +inf then HTTP Not Found
                # if x or y ==> -1 -1 then HTTP Bad Request, user just entered non digit values

                if (x >= 0 and x <= 9) and (y >= 0 and y <= 9):
                    x_bounderis = True
                    y_bounderis = True
                    formatted = True
                elif (x == -1) and (y == -1):
                    formatted = False
                # ==========================================================================

                if x_bounderis and y_bounderis: # http://127.0.0.1:5000/?x=5&y=5
                    
                    # FIRE
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()

                    # For a correctly formatted fire request your reply will be an HTTP OK message 
                    # with hit= followed by 1 (hit), or 0 (miss). If the hit results in a sink, then the response 
                    # will also include sink= followed by a letter code (C, B, R, S, D) of the sunk ship. 
                    # An example of such a reply is hit=1\&sink=D.

                    # Working with opponent board
                    # this function also tests whether it was [hit, miss, and sink]
                    # it will update my board and the opponent board
                    
                    message = updateOpponentBoard(x, y)
                    reply = "HTTP OK\n%s" % (message)

                    self.wfile.write( bytes(reply, "utf-8") )

                    # Print to console
                    print("======================================================")
                    print(reply)

                    return
                elif x_bounderis or not y_bounderis and formatted: # http://127.0.0.1:5000/?x=-1&y=10
                    # If the fire message includes coordinates that are out of bounds, 
                    # the response will be [HTTP Not Found]
                    self.send_error(404, "HTTP Not Found %s", self.path)
                    return
                elif not formatted:
                    # if the fire message is not formatted correctly, the response will be [HTTP Bad Request]
                    self.send_error(404, "HTTP Bad Request %s", self.path)
                    return
        except IOError:
            self.send_error(404, "HTTP Something Wrong %s", self.path)


# pull out values from the url
# the url has to be in this format: /?x=n&y=n
def parsURL(url):

    # initialize lis
    values = [None] * 2 

    # remove from the url first two chars: /?
    # now should be x=n&y=n
    url = url.replace("/?", "") 

    # split into two lines
    # should be x=n \n y=n
    multiline = re.split('&', url) 

    # remove x= and keep only digits
    x_line = multiline[0].replace("x=", "") 

    # remove y= and keep only digits
    y_line = multiline[1].replace("y=", "") 

    # try to pars string into digits
    try:
        x = int( x_line )
        y = int( y_line )

        values[0] = x
        values[1] = y

    except ValueError as e:

         # default values of the list if parssing did not work
        values[0] = -1
        values[1] = -1
        print(e)

    return values


# CONNECTION
# ====================================================================
# Initialize and start server
def start():
    try: 
        server = HTTPServer( (server_ip, port), httpServerHandler)
        print("\nSERVER: %s:%d" % (server_ip, port) )
        server.serve_forever()

    except KeyboardInterrupt:
        print("^C entered, server stopped")
        server.socket.close()

# ====================================================================



# [Working with own board]
# ***********************************************************************************************************

# After client send request, the server will update the game board of client and opponent board

# Generate own board html representation
def showOwnBoard():

    # The own board should be loaded again
    loadOwnBoard(ownFileName)

    tmp = ""
    html = ""

    # loop via game board 
    for i in range(board_size):
        for j in range(board_size):
            # build the line
            if j < (board_size - 1):
                tmp += "%c " % (ownBoard[i][j])
            elif j == (board_size - 1):
                # no space after the least char
                tmp += "%c" % (ownBoard[i][j])

        html += "<p>%s</p>" % (tmp)
        tmp = ""


    webPage = """
                <!DOCTYPE html>
                <html lang="en">
                    <head>
                        <title>Own Board</title>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1">

                        <link rel="stylesheet" href="css/own_board.css">
                    </head>
                    <body>
                        <div class="board">
                            <div class="name">Own Board</div>
                            <div class="ships">%s</div>
                        </div>

                        <script src="js/jquery_2_2_4_min.js" type="text/javascript"></script>
                        <script src="js/own_board.js" type="text/javascript"></script>
                    </body>
                </html>""" % (html)

    return webPage

# Load game board from the own_board.txt
def loadOwnBoard(fileName):

    # READ-TXT
    # =======================================================================================

    # store text lines in the list
    lines = [line.rstrip('\n') for line in open(fileName)]

    # number of lines
    length = len(lines)

    # Loop via lines list and
    # split each line into meaningful information
    for i in range(length):

        # store line[n] in the line
        line = lines[i]

        # convert the line into char list
        tmpList = list(line)

        # count number of elements in the list of chars
        size = len(tmpList)

        # loop via chars and store chars in the game board array
        for j in range(size):
            ownBoard[i][j] = tmpList[j]
    
    # =======================================================================================

# ***********************************************************************************************************

# [Working with opponent board]
# ***********************************************************************************************************

# Generate opponent board html representation
def showOpponentBoard():

    # The opponent board should be loaded again
    loadOpponentBoard(opponentFileName)

    # 2D List to store own board
    tmpBoard = [[0] * board_size for i in range(board_size)]

    tmp = ""
    html = ""

    # this loop is used to hide opponent ships
    # it will hide all ships with this symbol: _
    for i in range(board_size):
        for j in range(board_size):
            if (opponentBoard[i][j] != "*"):
                tmpBoard[i][j] = "_"
            elif (opponentBoard[i][j] == "*"):
                tmpBoard[i][j] = "*"

    # loop via tmpBoard and build html representation
    for i in range(board_size):
        for j in range(board_size):
            # build the line
            if j < (board_size - 1):
                tmp += "%c " % (tmpBoard[i][j])
            elif j == (board_size - 1):
                # no space after the least char
                tmp += "%c" % (tmpBoard[i][j])

        html += "<p>%s</p>" % (tmp)
        tmp = ""

    webPage = """
                <!DOCTYPE html>
                <html lang="en">
                    <head>
                        <title>Opponent Board</title>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1">

                        <link rel="stylesheet" href="css/own_board.css">
                    </head>
                    <body>
                        <div class="board">
                            <div class="name">Opponent Board</div>
                            <div class="ships">%s</div>
                        </div>

                        <script src="js/jquery_2_2_4_min.js" type="text/javascript"></script>
                        <script src="js/own_board.js" type="text/javascript"></script>
                    </body>
                </html>""" % (html)

    return webPage

# update opponent board
def updateOpponentBoard(i, j):

    global ownPoints

    # The opponent board should be loaded again
    loadOpponentBoard(opponentFileName)

    
    # ================================================================================================
    message = ""
    finalMessage = ""

    # results in a sink if no C, B, R, S, or D left [STATUS: NOT-IMPLEMENTED]

    # ships names
    ships = ["C", "B", "R", "S", "D"]

    # ships list size
    size = len(ships)

    # loop via board and find out if player hit or miss
    # and update the opponent board
    for x in range(size):
        if opponentBoard[i][j] == ships[x]:
            message = "hit=1\&sink=%s" % (ships[x])
            ownPoints += 1
            opponentBoard[i][j] = "*"
            break
        elif opponentBoard[i][j] == "_":
            opponentBoard[i][j] = "*"
            message = "hit=0"
            break
        elif opponentBoard[i][j] == "*":
            message = "HTTP Gone"
            break
    print("\nTEST: %s\n" % (message) )

    # save opponent board in to the text file
    saveOpponentBoard()
    # ================================================================================================

    # [Checking if this player has won]
    # ================================================================================================
    isShips = False
    # check if any ships left
    for row in range(board_size):
        for col in range(board_size):
            ship = opponentBoard[row][col]
            if (ship == "C") or (ship == "B") or (ship == "R") or (ship == "S") or (ship == "D"):
                if (ship != "_") and (ship != "*"):
                    print("SHIP: %s" % (ship) )
                    isShips = True
                    break
            ship = ""

    print("Is Ship: %r" % (isShips) )
    print("Points: %d" % (ownPoints) )
    # if no ships left return
    if isShips == False:
        finalMessage = "%s No more ships left: You one, your score is: %d." % (message, ownPoints)
        return finalMessage
    # ================================================================================================

    return message

# write new game board into the own_board.txt
def saveOpponentBoard():

    # WRITE: SAVE-CHANGES --> own_board.txt or opponent_board.txt
    # it depends what argument the server file got
    # ================================================
    # Store board in the txt file
    boardFile = open(opponentFileName,'w')

    # temporal string variable to store the line
    tmp = ""

    # loop via game board 
    for i in range(board_size):
        for j in range(board_size):
            # build the line
            tmp += "%c" % (opponentBoard[i][j])

        # save generated line into the txt file
        boardFile.write("%s\n" % (tmp) )
        
        # clean tmp variable
        tmp = ""

    boardFile.close()
    # ================================================

    return

# Load game board from the opponent_board.txt
def loadOpponentBoard(fileName):

    # READ-TXT
    # =======================================================================================

    # store text lines in the list
    lines = [line.rstrip('\n') for line in open(fileName)]

    # number of lines
    length = len(lines)

    # Loop via lines list and
    # split each line into meaningful information
    for i in range(length):

        # store line[n] in the line
        line = lines[i]

        # convert the line into char list
        tmpList = list(line)

        # count number of elements in the list of chars
        size = len(tmpList)

        # loop via chars and store chars in the game board array
        for j in range(size):
            opponentBoard[i][j] = tmpList[j]
    
    # =======================================================================================

# ***********************************************************************************************************

if __name__ == "__main__":

    # READ: arguments
    port = int(sys.argv[1])
    fileName = str(sys.argv[2])

    port = port
    ownFileName = fileName
    #opponentFileName = "opponent_board.txt"

    # the server.py should be executed twice
    # if server 1 got as argument own_board.txt then opponentFileName = opponent_board.txt
    # if server 1 got as argument opponent_board.txt then ownFileName = own_board.txt
    # The second instance of the server will do the same,
    # but if firs server instance got as argument own_board.txt
    # then second instance should get opponent_board.txt

    # First sever instance should be run: py .\server.py 5000 own_board.txt
    # Second sever instance should be run: py .\server.py 5001 opponent_board.txt

    # First client instance should with this url: 127.0.0.1:5001
    # Second client instance should with this url: 127.0.0.1:5000

    # It will flip the files names 
    if ownFileName == "own_board.txt":
        opponentFileName = "opponent_board.txt"
    elif ownFileName == "opponent_board.txt":
        opponentFileName = "own_board.txt"

    print("ownFileName: %s" % (ownFileName) )
    print("opponentFileName: %s" % (opponentFileName) )

    """
    scriptPath = os.path.realpath(__file__)
    homeFolderPath = os.path.dirname(scriptPath)
    print("\nHome folder path: \n%s" % (homeFolderPath) )
    """
    
    # read text file and load it into ownBoard list
    loadOwnBoard(ownFileName)

    # read text file and load it into opponentBoard list
    loadOpponentBoard(opponentFileName)

    # Start server
    start()