import socket
import threading
import queue
from threading import Thread
from time import sleep
import select
import sys
import json
from TicTacToeMessage import TicTacToeLoginMessage
from TicTacToeMessage import  TicTacToeStartStop
from TicTacToeMessage import TicTacToeGameMessage


player_dict = dict ()
player_symbol = ['X', 'O']
def checkWinner (move):
 
    count = 0;
    status = False
    row = [0,0,0]
    sum_diag = 0
    diag = [0,4,8]
    col = [0,0,0]
    total_set = 0
    while (count < 9):
        entry = []
        sum_row = 0
        index = (int)(count/3)
        for i in range (3):
            if (move [count +i] == 'X'):
                row [index] += 1
                col [i] += 1
                total_set +=1
                if ((count +i) in diag):
                    sum_diag += 1
            elif (move [count + i] == 'O'):
                total_set +=1
                row [index] += 4
                col [i] += 4
                if ((count +i) in diag):
                    sum_diag += 4
            elif (move [count + i]== ' '):
                row [index] += 0
                col [i] += 0
        count+=3

    if (3 in row or 12 in row) or (3 in col or 12 in col) or (sum_diag == 3 or sum_diag == 12):
        return (True,True)
    if (total_set == 9):
        status = True
    return (status, False)


def readLoop (readable, inputs, outputs, server, message_queues):
    # Handle inputs
    for s in readable:

        if s is server:
            # A "readable" server socket is ready to accept a connection
            connection, client_address = s.accept()
            print ("new connection from : %s ",  client_address)
            connection.setblocking(0)
            inputs.append(connection)

            # Give the connection a queue for data we want to send
            message_queues[connection] = queue.Queue()
        else:
            data = s.recv(1024)
            if data:
                # A readable client socket has data
               # print (s)
               # print (s.getpeername ())
               # print (str (s.getpeername ()[0])+":"+str (s.getpeername ()[1]))
                body = json.loads (data.decode ("utf-8"))
                if (body ['Action'] == 'LOGIN'):
                    msg = TicTacToeLoginMessage (body ['Player'], body ['Action'])
                    msg.setmsg (data)
                    player_dict [s] = msg.getPlayerName ()
                    if (len (player_dict) == 2):
                        start = TicTacToeStartStop ('START')
                        message_queues [s].put (start.getmsg())
                else:
                    message_queues[s].put (data)
                # Add output channel for response
                if s not in outputs:
                    outputs.append(s)
            else:
                # Interpret empty result as closed connection
               # print >>sys.stderr, 'closing', client_address, 'after reading no data'
                # Stop listening for input on the connection
                if s in outputs:
                    outputs.remove(s)
                inputs.remove(s)
                s.close()

                # Remove message queue
                del message_queues[s]
                if s in player_dict.keys ():
                    del player_dict [s]
                stop = TicTacToeStartStop ('STOP')
                for sockt,m in message_queues.items ():
                    m.put (stop.getmsg ())
   
def writeLoop (message_queues, outputs):
    
    
    for m in message_queues:
        size = 0
        if (not message_queues [m].empty ()):
            size = message_queues [m].qsize ();
        while (size > 0):
            item = message_queues [m].get (False, None)
            body = json.loads (item)
            if (body ['Action'] == 'START' and len(player_dict) == 2):
                
                for sock, player in player_dict.items():
                    if (sock != m):
                        player_msg_1 = TicTacToeGameMessage (player_dict [m], 'PLAYER_TURN')
                        player_msg_1.setPlayer1 (player, player_symbol [0])
                        player_msg_1.setPlayerTurn (player)


                for sock, player in player_dict.items():
                    if (sock == m):
                        player_msg_1.setPlayer2 (player, player_symbol [1])                        
                move = []
                for i in range (9): 
                    move.append (' ')
                player_msg_1.setPlayerMove (move)
                    
                for s in outputs:
                    s.send (player_msg_1.getmsg ())
            elif (body ['Action'] == 'STOP'):
                player_msg_1 = TicTacToeGameMessage ('None', 'GAME_VOID')
                for s in outputs:
                    s.send (player_msg_1.getmsg ())
                player_dict.clear ()
            elif  (body ['Action'] == 'SERVER_TURN'):
                player_msg = TicTacToeGameMessage ()
                player_msg.setmsg (item)
                status = checkWinner (player_msg.getPlayerMove ())
                if (status [0]):
                    if (status [1]):
                        print (" We have winnder ", player_msg.getPlayerTurn ())
                    else:
                        print ("We have Tie")
                        player_msg.setPlayerTurn ("None (Tie)")
                    player_msg.setPlayerAction('GAME_RESULT')
                    player_dict.clear ()
                else:
                    for player in player_dict.values ():
                        if (player != player_msg.getPlayerTurn ()):
                            player_msg.setPlayerTurn (player)
                            break
                    player_msg.setPlayerAction ('PLAYER_TURN')
                for s in outputs:
                    s.send (player_msg.getmsg ())
            size-=1
                

def exceptLoop (s):
    pass

def serverLoop (server):
    read_fd = [server]
    write_fd = []
    except_fd = []
    message_queues = {}
    while (1):
        readlist,writelist,except_list = select.select (read_fd, write_fd,read_fd,None)

        readLoop (readlist, read_fd, write_fd, server, message_queues)

        writeLoop (message_queues, write_fd)

        exceptLoop (server)

def ServerMain ():
    s = socket.socket()         # Create a socket object
    host = socket.gethostname() # Get local machine name
    port = 50000                # Reserve a port for your service.

    print ('Server started!')
    print ('Waiting for clients...')

    s.bind((host, port))        # Bind to the port
    s.listen(2)                 # Now wait for client connection.
    thread = Thread(target = serverLoop, args = (s,))
    thread.start()
    thread.join()


if __name__ == '__main__':
    ServerMain ()