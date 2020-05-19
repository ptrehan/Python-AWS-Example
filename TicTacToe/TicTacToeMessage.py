import json
from enum import Enum

class TicTacToeStartStop:
    def __init__ (self, action):
        self._action  = action;
    def getmsg (self):
        return json.JSONEncoder ().encode ({'Action':self._action}).encode ("utf-8")

class TicTacToeLoginMessage:
    login_dict = dict ()
    valid_list = ['Player', 'Action']

    def __init__ (self, name, action):
        self.login_dict ['Player'] = name
        self.login_dict ['Action'] = action

    def getPlayerAction (self):
        return (self.login_dict ['Action'])

    def getPlayerName (self):
        return self.login_dict ['Player']

    def isValid (self):
        for item in valid_list:
            if (not item in login_dict):
                return False
        return True

    def getmsg (self):
        return json.JSONEncoder ().encode (self.login_dict).encode ("utf-8")

    def setmsg (self, data):
        msg = data.decode ("utf-8")
        self.login_dict = json.loads (msg)

# Action = 'PLAYER_TURN' -> message from server to player
# Action = 'SERVER_TURN' -> message from player to server
# Action = 'GAME_RESULT' -> message from server to player 
# Action = 'NEW_GAME' -> message from 
class TicTacToeGameMessage:
    player_dict = dict ()

    def __init__ (self, name='', action=''):
        self.player_dict ['Player'] = name
        self.player_dict ['Action'] = action

    def setPlayer1 (self,name, symbol):
        self.player_dict ['Player1'] = name
        self.player_dict ['Symbol1'] = symbol
    def getPlayer1(self):
        return (self.player_dict ['Player1'], self.player_dict ['Symbol1'])

    def setPlayer2 (self,name, symbol):
        self.player_dict ['Player2'] = name
        self.player_dict ['Symbol2'] = symbol
    def getPlayer2(self):
        return (self.player_dict ['Player2'], self.player_dict ['Symbol2'])

    def setPlayerTurn (self,name):
        self.player_dict ['Turn'] = name
    def getPlayerTurn(self):
        return self.player_dict ['Turn']

    def setPlayerMove (self,move):
        self.player_dict ['Moves'] = move
    def getPlayerMove (self):
        return self.player_dict ['Moves']

    def setPlayerAction(self,action):
        self.player_dict ['Action'] = action
    def getPlayerAction(self):
        return self.player_dict ['Action']

    def setPlayerName(self,name):
        self.player_dict ['Player'] = name
    def getPlayerName(self):
        return self.player_dict ['Player']

    def getmsg (self):
        #self.player_dict ['Player'] = getPlayerName ()
        #self.player_dict ['Action'] = getPlayerAction ()
        return json.JSONEncoder ().encode (self.player_dict).encode ('utf-8')

    def setmsg (self, data):
        msg = data.decode ('utf-8')
        self.player_dict = json.loads (msg)