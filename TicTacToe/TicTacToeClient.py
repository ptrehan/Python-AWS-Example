import socket
from TicTacToeMessage import TicTacToeLoginMessage
import json
from TicTacToeMessage import TicTacToeGameMessage

def displayBoard (moves):
    count = 0;
    empty_cells = []
    while (count < 9):
        output = ""
        for i in range(3):
            if (moves [count+i] == ' '):
                output+='_'
                empty_cells.append (count+i+1)
            else:
                output+=moves[count+i]
            output+=" "
        print (output)
        count+=3
    return empty_cells

def ClientMain ():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = socket.gethostname() # Get local machine name
    port = 50000                # Reserve a port for your service.
    s.connect ((host,port))
    st = str (s)
    print (st)
    
    name = input ("Please enter player name:")
    keepPlaying = True
    while (keepPlaying):
        print ('Starting New Game')
        loginmsg = TicTacToeLoginMessage (name, 'LOGIN')
        s.send (loginmsg.getmsg ())
        keepPlaying = False
        gameDone = False
        while (not gameDone):
            data = s.recv (1024)
            msg = data.decode ('utf-8')
            print (msg)
            body = json.loads (msg)
            if (body ['Action'] == 'PLAYER_TURN'):
                msg = TicTacToeGameMessage ()
                msg.setmsg (data)
                print (msg.getPlayer1 ()[0] + " symbol :" + msg.getPlayer1 ()[1])
                print (msg.getPlayer2 ()[0] + " symbol :" + msg.getPlayer2 ()[1])

                if (name == msg.getPlayer1 ()[0]):
                    sign = msg.getPlayer1 ()[1]
                else:
                    sign = msg.getPlayer2 ()[1]

                moves = msg.getPlayerMove ()
                empty_cells = displayBoard (moves)
                if (msg.getPlayerTurn () == name):
                    print (msg.getPlayerTurn (), ' Turn')
                    while (1):
                        print ('Valid Moves = ', empty_cells)
                        choice = input ("Please enter your turn:")

                        if (not choice.isdigit ()):
                            print ("invalid choice. Try again")
                            continue
                        choice = int(choice)
                        if (choice in empty_cells):
                            moves [choice -1] = sign
                            break
                        else:
                            print ("invalid choice. Try again")
                    displayBoard (moves)
                    msg.setPlayerMove (moves)
                    msg.setPlayerAction ('SERVER_TURN')
                    s.send (msg.getmsg ())
                else:
                    print ('Waiting for ', msg.getPlayerTurn ())
            elif (body ['Action'] == 'GAME_RESULT'):
                msg = TicTacToeGameMessage ()
                msg.setmsg (data)
                print ('Winner is ',msg.getPlayerTurn ())
                choice = input ("Do you want to play again [Y/y]")
                if (choice.upper () == 'Y'):
                    keepPlaying = True
                gameDone = True
            elif (body ['Action'] == 'GAME_VOID'):
                print ('Game is Void')
                choice = input ("Do you want to play again [Y/y]")
                if (choice.upper () == 'Y'):
                    keepPlaying = True
                gameDone = True


if __name__ == '__main__':
    ClientMain ()
