g_nextClientId = 0

def GetNextId():
    global g_nextClientId
    
    g_nextClientId += 1
    return g_nextClientId

class Client:
    def __init__(this, socket):
        global g_nextClientId
        this.socket = socket
        this.id = GetNextId()

g_clients = dict()

def AddClient(client):
    global g_clients
    g_clients[client.id] = client

def GetClient(id):
    global g_clients
    return g_clients[id]

def RemoveClient(id):
    g_clients.pop(id)
