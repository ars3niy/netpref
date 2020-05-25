import clientmanager
import functools
import os
import imp

class Variable:
    def __init__(this, name, value):
        this.name = name
        this.value = value
        this.extra = None

def DecodeArgs(s, amount):
    w = SplitAndDecode(s)
    if len(w) == amount:
        if amount == 1:
            return w[0]
        else:
            return w

class GameApi:
    def __init__(this, name):
        this.name = name
        this.players = []
        this.eStartGame = Events.eStartGame
        this.stWaitingForStart = States.stWaitingForStart;
    
    def Create(this):
        raise "Please implement"
    
    def GetTypeName(this):
        raise "Please implement"
    
    def GetPlayerCount(this):
        raise "Please implement"
    
    def AddCommand(this):
        this.nextCustomCommand += 1
        return Command(this.nextCustomCommand-1)
    
    def DefineCommand(this, commandStr, command, decoder, handler):
        this.commands[commandStr] = [command, decoder]
        this.commandHandlers[command] = handler
    
    def AddEvent(this):
        this.nextCustomEvent += 1
        return Event(this.nextCustomEvent-1)
    
    def Event(this, event, state, handler):
        this.eventHandlers += [[event, state, handler]]
    
    def AddState(this, name):
        this.nextCustomState += 1
        return State(name, this.nextCustomState-1)
    
    def SetState(this, state):
        if state == States.stAny:
            raise "No thanks"
        this.state = state

    def HandleEvent(this, event, arg):
        selectedHandler = None
        for handlerItem in this.eventHandlers:
            [e, s, h] = handlerItem
            if (e == event) and ((s == this.state) or ((s == States.stAny) and (selectedHandler == None))):
                selectedHandler = h
        if selectedHandler != None:
            selectedHandler(arg)
        else:
            print("game", this.name, "cannot handle event", event.value, "in state", this.state.name)
    
    def AddVar(this, name):
        this.varIndex[name] = len(this.variables)
        this.variables += [Variable(name, "")]
    
    def GetVar(this, name):
        return this.variables[this.varIndex[name]].value
    
    def SetVar(this, name, value):
        if not name in this.varIndex:
            this.AddVar(name)
        this.variables[this.varIndex[name]].value = value
    
    def SetVarExtra(this, name, extra):
        if not name in this.varIndex:
            this.AddVar(name)
        this.variables[this.varIndex[name]].extra = extra
    
    def GetVarExtra(this, name):
        return this.variables[this.varIndex[name]].extra
    
    def GetVarValueForPlayer(this, value, extra, clientId):
        return value
    
class Event:
    def __init__(this, value):
        this.value = value

class EventsType:
    def __init__(this):
        this.eDisconnected = Event(0)
        this.eConnected = Event(1)
        this.eExploded = Event(2)
        this.eStartGame = Event(3)
        
    def getFirstCustom(this):
        return 4

Events = EventsType()

class Command:
    def __init__(this, value):
        this.value = value

class CommandsType:
    def __init__(this):
        this.cmdCreateGame = Command(0)
        this.cmdJoinGame = Command(1)
        
    def getFirstCustom(this):
        return 2

Commands = CommandsType()

class State:
    def __init__(this, name, value):
        this.name = name
        this.value = value

class StatesType:
    def __init__(this):
        this.stAny = State("Any", 0)
        this.stWaitingForStart = State("WaitStart", 1)
        this.stWaitingForPlayers = State("WaitPlayers", 2)
        this.stLobby = State("Lobby", 3)
        
    def getFirstCustom(this):
        return 4

States = StatesType()

class Game(GameApi):
    def __init__(this, name):
        GameApi.__init__(this, name)
        this.state = States.stWaitingForStart
        this.stateBeforeDisconnect = this.state
        this.commands = dict()
        this.commandHandlers = dict()
        this.eventHandlers = []
        this.clients = dict()
        this.nextCustomEvent = Events.getFirstCustom()
        this.nextCustomCommand = Commands.getFirstCustom()
        this.nextCustomState = States.getFirstCustom()
        this.playerNames = []
        this.varIndex = dict()
        this.variables = []

        this.Create()
        this.Event(Events.eConnected, States.stWaitingForStart, this.NewPlayer)
        this.Event(Events.eConnected, States.stWaitingForPlayers, this.PlayerReturned)
        this.Event(Events.eDisconnected, States.stAny, this.PlayerLost)
        this.Event(Events.eDisconnected, States.stWaitingForStart, this.PlayerLeft)
        this.Event(Events.eExploded, States.stAny, this.GameException)
    
    def AddClient(this, client):
        this.clients[client.id] = client
    
    def RemoveClient(this, clientId):
        this.clients.pop(clientId)
    
    def GetClients(this):
        result = [this.clients[cid] for cid in this.clients]
        result.sort(key=lambda c: c.id)
        return result
    
    def HasClient(this, clientId):
        return clientId in this.clients
    
    def SendUpdate(this):
        for clientId in this.clients:
            this.clients[clientId].SendMessage(this.Encode(clientId))
    
    def GameException(this, arg):
        [clientid, backtrace] = arg
        print("Exception raised")
        print(backtrace)
    
    def PlayerLost(this, clientId):
        clientName = this.clients[clientId].name
        if this.state != States.stWaitingForPlayers:
            print("Suspending game", this.name, "due to loss of player", clientName)
            this.stateBeforeDisconnect = this.state
        this.SetState(States.stWaitingForPlayers)
        
        this.players[this.playerNames.index(clientName)] = None
        this.RemoveClient(clientId)

        if len(this.clients) == 0:
            lobbyGame.RemoveGame(this)
        else:
            this.SendUpdate()
    
    def NewPlayer(this, client):
        this.AddClient(client)
        this.players += [client]
        this.playerNames += [client.name]
        
        if len(this.clients) == this.GetPlayerCount():
            print("Start game", this.name, "(has enough players)")
            this.HandleEvent(Events.eStartGame, None)
        else:
            this.SendUpdate()
    
    def PlayerReturned(this, client):
        if not client.name in this.playerNames:
            print("Player", client.name, "was not in game", this.name, "when it was suspended")
            return
        this.AddClient(client)
        this.players[this.playerNames.index(client.name)] = client
        if len(this.clients) == this.GetPlayerCount():
            print("Resume game", this.name, "(all players returned)")
            this.SetState(this.stateBeforeDisconnect)
        this.SendUpdate()
    
    def PlayerLeft(this, clientId):
        clientName = this.clients[clientId].name
        ind = this.playerNames.index(clientName)
        this.players.pop(ind)
        this.playerNames.pop(ind)
        this.RemoveClient(clientId)
        
        if len(this.clients) == 0:
            lobbyGame.RemoveGame(this)
        else:
            this.SendUpdate()
    
    def Encode(this, clientId):
        s = "State=" + this.state.name
        if this.state == States.stWaitingForStart:
            for name in this.playerNames:
                s += " player=" + EncodeString(name)
        elif this.state == States.stWaitingForPlayers:
            for i in range(len(this.players)):
                if this.players[i] == None:
                    s += " missing=" + EncodeString(this.playerNames[i])
        else:
            for var in this.variables:
                if var.value != None:
                    strValue = str(this.GetVarValueForPlayer(var.value, var.extra, clientId))
                    if len(strValue) > 0:
                        s += " " + var.name + "=" + EncodeString(strValue)
        return s
        
    def DecodeCommand(this, commandStr, argStr):
        if commandStr in this.commands:
            arg = this.commands[commandStr][1](argStr)
            if arg == None:
                print("Game", this.name, "failed to decode argument", "'"+argStr+"'", "for command", commandStr)
                return [None, None]
            else:
                return [this.commands[commandStr][0], arg]
        else:
            print("Game", this.name, "unknown command", commandStr)
            return [None, None]
    
    def HandleCommand(this, clientId, cmd, arg):
        if cmd in this.commandHandlers:
            this.commandHandlers[cmd](this.clients[clientId], arg)
        
def ConnectionAck():
    return "ack"

def FailMessage():
    return "nak"

def EncodeString(s):
    body = map(lambda c: "\\\"" if c=="\"" else "\\\\" if c=="\\" else c, s)
    return "\"" + functools.reduce(lambda s1, s2: s1+s2, body, "") + "\""

def SplitAndDecode(s):
    s = s.strip()
    result = []
    while len(s) > 0:
        if s[0] != "\"":
            [token, space, s] = s.partition(" ")
            s = s.strip()
            result += [token]
        else:
            i=1
            token=""
            while (i < len(s)) and (s[i] != "\""):
                if s[i] == "\\" and (i+1 > len(s)):
                    if s[i+1] == "\"":
                        token += "\""
                        i += 2
                    elif s[i+1] == "\\":
                        token += "\\"
                        i += 2
                    else:
                        token += s[i]
                        i += 1
                else:
                    token += s[i]
                    i += 1
                
            result += [token]
            s = s[i+1:].strip()
    return result

def DecodeOne(s):
    return DecodeArgs(s, 1)

def DecodeTwo(s):
    return DecodeArgs(s, 2)

class LobbyGame(Game):
    def Create(this):
        this.cmdName = this.AddCommand()
        this.games = dict()
        this.DefineCommand("name", this.cmdName, DecodeOne, this.NamePlayer)
        this.DefineCommand("creategame", Commands.cmdCreateGame, DecodeTwo, this.CreateGame)
        this.DefineCommand("join", Commands.cmdJoinGame, DecodeOne, this.JoinGame)
        this.Event(Events.eDisconnected, States.stLobby, this.ClientDisconnected)
        this.SetState(States.stLobby)
    
    def GetPlayerCount(this):
        return 0
    
    def GameException(this, arg):
        [clientId, backtrace] = arg
        if clientId:
            this.clients[clientId].SendMessage(EncodeException(backtrace))
        else:
            for client in this.clients:
                client.SendMessage(EncodeException(backtrace))
    
    def ClientDisconnected(this, clientId):
        this.RemoveClient(clientId)
        this.SendUpdate()
    
    def Encode(this, clientId):
        s = ""
        for client in this.GetClients():
            if client.name:
                s += " player=" + EncodeString(client.name)
        for gameName in this.games:
            game = this.games[gameName]
            s += " game=" + EncodeString(game.name) + " type=" + EncodeString(game.GetTypeName())
        return s
    
    def NameExists(this, name):
        for otherClientId in this.clients:
            if this.clients[otherClientId].name == name:
                print("Client named", name, "already exists in the lobby")
                return True
        for gameName in this.games:
            for otherClient in this.games[gameName].GetClients():
                if otherClient.name == name:
                    print("Client named", name, "already exists in game", gameName)
                    return True

    def NamePlayer(this, client, arg):
        print(client.id, "named as", arg)
        if client.name == arg:
            pass
        elif this.NameExists(arg):
            client.SendMessage(FailMessage())
        else:
            client.SetName(arg)
            this.SendUpdate()
    
    def CreateGame(this, client, arg):
        [gameName, gameType] = arg
        
        if not client.name:
            print(client.id, "wants to create game but does not have a name")
            client.SendMessage(FailMessage())
            return
        
        if gameName in this.games:
            print("game", gameName, "already exists")
            client.SendMessage(FailMessage())
            return

        if not gameType in gameModules:
            print("Game type", gameType, "is unknown")
            client.SendMessage(FailMessage())
            return
        
        newGame = gameModules[gameType].Game(gameName)
        this.games[gameName] = newGame
        
        newGame.HandleEvent(Events.eConnected, client)
        if newGame.HasClient(client.id):
            print("client", client.name, "created and joined game", gameName)
            client.SetGame(newGame)
            this.RemoveClient(client.id)
            this.SendUpdate()
        else:
            print("client", client.name, "failed to join his own game")
            this.games.pop(gameName)
            client.SendMessage(FailMessage())
    
    def RemoveGame(this, game):
        print("Removing game", game.name)
        this.games.pop(game.name)
        this.SendUpdate()
    
    def JoinGame(this, client, arg):
        gameName = arg
        
        if not client.name:
            print(client.id, "wants to join game but does not have a name")
            client.SendMessage(FailMessage())
            return

        if not gameName in this.games:
            print("game", gameName, "does not exist")
            client.SendMessage(FailMessage())
            return
        
        newGame = this.games[gameName]
        newGame.HandleEvent(Events.eConnected, client)

        if newGame.HasClient(client.id):
            print("client", client.name, "joined game", gameName)
            client.SetGame(newGame)
            this.RemoveClient(client.id)
            this.SendUpdate()
        else:
            print("client", client.name, "failed to join game", gameName)
            client.SendMessage(FailMessage())

lobbyGame = LobbyGame("lobby")
gameModules = dict()

def EncodeGameTypes():
    s = "ack=\"\""
    for gameType in gameModules:
        s += " gametype=" + EncodeString(gameType)
    return s

def AttachClient(client):
    client.SetGame(lobbyGame)
    lobbyGame.AddClient(client)
    client.SendMessage(EncodeGameTypes())

def LoadGameModules(path):
    for filename in os.listdir(path):
        if filename.endswith(".py"):
            basename = filename.rpartition(".")[0]
            [file, p, desc] = imp.find_module(basename, [path])
            mod = imp.load_module("gameplugins." + basename, file, p, desc)
            try:
                gameType = mod.Game.GetTypeName(None)
            except:
                print("Skipped game module", filename, "(not a game plugin)")
                continue
            
            print("Found game", gameType, "in module", filename)
            gameModules[gameType] = mod
