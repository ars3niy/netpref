#!/usr/bin/python3

import websockets
import asyncio
import traceback
import clientmanager
import games

class Client(clientmanager.Client):
    def __init__(this, socket):
        clientmanager.Client.__init__(this, socket)
        this.game = None
        this.outbox = []
        this.name = None
        this.socket = socket
    
    def SetGame(this, game):
        this.game = game
    
    def GetGame(this):
        return this.game
    
    def SetName(this, name):
        this.name = name
    
    def HandleMessage(this, message):
        [commandStr, space, argStr] = map(lambda s: s.strip(), message.partition(" "))
        
        [command, args] = this.game.DecodeCommand(commandStr, argStr)
        if command != None:
            this.game.HandleCommand(this.id, command, args)
    
    def SendMessage(this, message):
        this.outbox += [message]
        
    @asyncio.coroutine
    def SendQueuedMessages(this):
        for message in this.outbox:
            yield from this.socket.send(message)
        this.outbox = []

@asyncio.coroutine
def HandleGameException(client, clientAlive=True):
        error = traceback.format_exc()
        print("Exception caught")
        print(error)
        try:
            client.GetGame().HandleEvent(games.Events.eExploded, [client.id if clientAlive else None, error])
            if clientAlive:
                yield from client.SendQueuedMessages()
            else:
                for otherClient in client.GetGame().GetClients():
                    try:
                        yield from otherClient.SendQueuedMessages()
                    except websockets.ConnectionClosed:
                        pass
                    except:
                        raise
        except websockets.ConnectionClosed:
            pass
        except:
            print("Exception while handling exception")
            print(traceback.format_exc())

@asyncio.coroutine
def ClientReceiver(client):
    try:
        clientmanager.AddClient(client)
        games.AttachClient(client)
        while True:
            message = yield from client.socket.recv()
            client.HandleMessage(message)
    except websockets.ConnectionClosed:
        print("Client disconnected id", client.id)
        try:
            clientmanager.RemoveClient(client.id)
            client.GetGame().HandleEvent(games.Events.eDisconnected, client.id)
        except:
            yield from HandleGameException(client, False)
    except:
        yield from HandleGameException(client)

@asyncio.coroutine
def ClientSubmitter(client):
    try:
        while True:
            yield from asyncio.sleep(0.1)
            yield from client.SendQueuedMessages()
    except websockets.ConnectionClosed:
        # Receiver will take care of this
        pass

@asyncio.coroutine
def ClientHandler(socket, path):
    client = Client(socket)
    print("Client connected id", client.id)
    
    receiverTask = asyncio.async(ClientReceiver(client))
    submitterTask = asyncio.async(ClientSubmitter(client))
    
    done, pending = yield from asyncio.wait([receiverTask, submitterTask], \
                                            return_when=asyncio.FIRST_COMPLETED)

    for task in pending:
        task.cancel()

games.LoadGameModules(str(__file__).rpartition("/")[0] + "/gamemodules")

start_server = websockets.serve(ClientHandler, port=8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
