#!/usr/bin/python3

import websockets
import asyncio
from games import EncodeString

PORT=8765
GAMETYPE="rostovtest"

@asyncio.coroutine
def Recv(socket, expected=None):
    response = yield from asyncio.wait_for(socket.recv(), 2)
    if (expected != None) and (response.strip() != expected.strip()):
        raise Exception("\nExpected: '" + expected + "'\nreceived: '" + response + "'")

@asyncio.coroutine
def DontReceive(socket):
    response = None
    try:
        response = yield from asyncio.wait_for(socket.recv(), 0.5)
    except:
        pass
    if response:
        raise Exception("Received unexpected response: '" + response + "'")

@asyncio.coroutine
def Connect():
    return websockets.connect("ws://localhost:" + str(PORT))

@asyncio.coroutine
def InitialMessage(socket):
    response = yield from asyncio.wait_for(socket.recv(), 2)
    words = response.strip().split()
    if words[0] != "ack=\"\"":
        raise Exception("Initial string: '" + response + "' doesn't start with ack")
    if words.count("gametype=\"rostovtest\"") != 1:
        raise Exception("Initial string: '" + response + "' doesn't contain one rostovtest")

@asyncio.coroutine
def Nak(socket):
    yield from Recv(socket, "nak")

@asyncio.coroutine
def LobbyState(socket, players, games=[]):
    response = ""
    for player in players:
        response += " player=" + EncodeString(player)
    for game in games:
        response += " game=" + EncodeString(game) + " type=" + EncodeString(GAMETYPE)
    yield from Recv(socket, response)

@asyncio.coroutine
def GameWaitStartState(socket, players):
    response = "State=WaitStart"
    for player in players:
        response += " player=" + EncodeString(player)
    yield from Recv(socket, response)

@asyncio.coroutine
def GameWaitPlayerState(socket, missingPlayers):
    response = "State=WaitPlayers"
    for player in missingPlayers:
        response += " missing=" + EncodeString(player)
    yield from Recv(socket, response)

@asyncio.coroutine
def GameState(socket, state, position, speaker=None, p=None, g=None, v=None, \
              card0=None, card1=None, card2=None, cardbuy=None, \
              choice=None, ready=None, tomove=None, move=None, takes=None,
              wantsFinish=None, shares=None):
    r = "State=" + state
    r += " position=" + EncodeString(str(position))
    r += " player0=" + EncodeString("player1") + " player1=" + EncodeString("player2") + " player2=" + EncodeString("player3");
    if speaker:
        r += " speaker=" + EncodeString(str(speaker))
    
    vind=0
    for i in range(3):
        r += " p%d=" % (i) + EncodeString(str(p[i] if p else 0))
        r += " g%d=" % (i) + EncodeString(str(g[i] if g else 0))
        for j in range(3):
            if j != i:
                r += " v%d%d=" % (i,j) + EncodeString(str(v[vind] if v else 0))
                vind += 1
    if card0:
        r += " cards0=" + EncodeString(card0)
    if card1:
        r += " cards1=" + EncodeString(card1)
    if card2:
        r += " cards2=" + EncodeString(card2)
    if cardbuy:
        r += " buy=" + EncodeString(cardbuy)

    if move and (move[0] != None):
        r += " move0=" + EncodeString(move[0])
    if move and (move[1] != None):
        r += " move1=" + EncodeString(move[1])
    if move and (move[2] != None):
        r += " move2=" + EncodeString(move[2])
    
    if choice and choice[0]:
        r += " choice0=" + EncodeString(choice[0])
    if choice and choice[1]:
        r += " choice1=" + EncodeString(choice[1])
    if choice and choice[2]:
        r += " choice2=" + EncodeString(choice[2])
    
    if ready and (ready[0] != None):
        r += " ready0=" + EncodeString(str(ready[0]))
    if ready and (ready[1] != None):
        r += " ready1=" + EncodeString(str(ready[1]))
    if ready and (ready[2] != None):
        r += " ready2=" + EncodeString(str(ready[2]))
    
    if takes and (takes[0] != None):
        r += " take0=" + EncodeString(str(takes[0]))
    if takes and (takes[1] != None):
        r += " take1=" + EncodeString(str(takes[1]))
    if takes and (takes[2] != None):
        r += " take2=" + EncodeString(str(takes[2]))
    
    if shares and (shares[0] != None):
        r += " share0=" + EncodeString(str(shares[0]))
    if shares and (shares[1] != None):
        r += " share1=" + EncodeString(str(shares[1]))
    if shares and (shares[2] != None):
        r += " share2=" + EncodeString(str(shares[2]))
    
    if tomove != None:
        r += " tomove=" + EncodeString(str(tomove))
    
    if wantsFinish != None:
        r += " wantfinish=" + EncodeString(wantsFinish)
    
    yield from Recv(socket, r)

@asyncio.coroutine
def GameStartState(s1, s2, s3, p=None, g=None, v=None):
    yield from GameState(s1, "Trade", 0, speaker=1,
                         card0="Qd Qh Ks Kc Kd Kh As Ac Ad Ah", \
                         card1="*10", \
                         card2="*10", 
                         cardbuy="*2",
                         p=p, g=g, v=v)
    yield from GameState(s2, "Trade", 1, speaker=1, \
                         card0="*10", 
                         card1="Ts Tc Td Th Js Jc Jd Jh Qs Qc", \
                         card2="*10", \
                         cardbuy="*2",
                         p=p, g=g, v=v)
    yield from GameState(s3, "Trade", 2, speaker=1, \
                         card0="*10", \
                         card1="*10", \
                         card2="7d 7h 8s 8c 8d 8h 9s 9c 9d 9h", \
                         cardbuy="*2",
                         p=p, g=g, v=v)

@asyncio.coroutine
def CreateGameTest():
    s1 = yield from Connect()
    yield from InitialMessage(s1)
    yield from s1.send("name player1")
    yield from LobbyState(s1, ["player1"])
    
    s2 = yield from Connect()
    yield from InitialMessage(s2)
    yield from s2.send("name player1")
    yield from Nak(s2)
    yield from s2.send("name player2")
    yield from LobbyState(s1, ["player1", "player2"])
    yield from LobbyState(s2, ["player1", "player2"])
    
    yield from s2.send("creategame game1 " + GAMETYPE)
    yield from GameWaitStartState(s2, ["player2"])
    yield from LobbyState(s1, ["player1"], ["game1"])
    
    s3 = yield from Connect()
    yield from InitialMessage(s3)
    yield from s3.send("name player2")
    yield from Nak(s3)
    yield from s3.send("name player3")
    yield from LobbyState(s1, ["player1", "player3"], ["game1"])
    yield from LobbyState(s3, ["player1", "player3"], ["game1"])
    
    yield from s1.send("join game1")
    yield from GameWaitStartState(s2, ["player2", "player1"])
    yield from LobbyState(s3, ["player3"], ["game1"])
    yield from GameWaitStartState(s1, ["player2", "player1"])
    
    yield from s2.close()
    yield from GameWaitStartState(s1, ["player1"])

    yield from s1.close()
    yield from LobbyState(s3, ["player3"])
    
    yield from s3.close()

@asyncio.coroutine
def StartGameTest():
    s1 = yield from Connect()
    yield from InitialMessage(s1)
    yield from s1.send("name player1")
    yield from LobbyState(s1, ["player1"])
    yield from s1.send("creategame game1 " + GAMETYPE)
    yield from GameWaitStartState(s1, ["player1"])

    s2 = yield from Connect()
    yield from InitialMessage(s2)
    yield from s2.send("name player2")
    yield from LobbyState(s2, ["player2"], ["game1"])
    yield from s2.send("join game1")
    yield from GameWaitStartState(s1, ["player1", "player2"])
    yield from GameWaitStartState(s2, ["player1", "player2"])

    s3 = yield from Connect()
    yield from InitialMessage(s3)
    yield from s3.send("name player3")
    yield from LobbyState(s3, ["player3"], ["game1"])
    yield from s3.send("join game1")
    
    yield from GameState(s1, "Trade", 0, speaker=1,
                         card0="Qd Qh Ks Kc Kd Kh As Ac Ad Ah", \
                         card1="*10", \
                         card2="*10", 
                         cardbuy="*2")
    yield from GameState(s2, "Trade", 1, speaker=1, \
                         card0="*10", 
                         card1="Ts Tc Td Th Js Jc Jd Jh Qs Qc", \
                         card2="*10", \
                         cardbuy="*2")
    yield from GameState(s3, "Trade", 2, speaker=1, \
                         card0="*10", \
                         card1="*10", \
                         card2="7d 7h 8s 8c 8d 8h 9s 9c 9d 9h", \
                         cardbuy="*2")
    
    yield from s3.close()
    yield from GameWaitPlayerState(s1, ["player3"])
    yield from GameWaitPlayerState(s2, ["player3"])
    
    yield from s1.close()
    yield from GameWaitPlayerState(s2, ["player1", "player3"])
    
    s3 = yield from Connect()
    yield from InitialMessage(s3)
    yield from s3.send("name player3_new")
    yield from LobbyState(s3, ["player3_new"], ["game1"])
    yield from s3.send("join game1")
    yield from Nak(s3)
    
    yield from s3.send("name player3")
    yield from LobbyState(s3, ["player3"], ["game1"])
    yield from s3.send("join game1")
    yield from GameWaitPlayerState(s2, ["player1"])
    yield from GameWaitPlayerState(s3, ["player1"])
    
    s1 = yield from Connect()
    yield from InitialMessage(s1)
    yield from s1.send("name player1_new")
    yield from LobbyState(s1, ["player1_new"], ["game1"])
    yield from s1.send("join game1")
    yield from Nak(s1)
    
    yield from s1.send("name player1")
    yield from LobbyState(s1, ["player1"], ["game1"])
    yield from s1.send("join game1")

    yield from GameState(s1, "Trade", 0, speaker=1,
                         card0="Qd Qh Ks Kc Kd Kh As Ac Ad Ah", \
                         card1="*10", \
                         card2="*10", 
                         cardbuy="*2")
    yield from GameState(s2, "Trade", 1, speaker=1, \
                         card0="*10", 
                         card1="Ts Tc Td Th Js Jc Jd Jh Qs Qc", \
                         card2="*10", \
                         cardbuy="*2")
    yield from GameState(s3, "Trade", 2, speaker=1, \
                         card0="*10", \
                         card1="*10", \
                         card2="7d 7h 8s 8c 8d 8h 9s 9c 9d 9h", \
                         cardbuy="*2")

    
    yield from s1.close()
    yield from s2.close()
    yield from s3.close()

@asyncio.coroutine
def RepeatNameTest():
    s1 = yield from Connect()
    yield from InitialMessage(s1)
    yield from s1.send("name player1")
    yield from LobbyState(s1, ["player1"])
    yield from s1.send("name player1")
    yield from DontReceive(s1)
    
    yield from s1.send("name player1_new")
    yield from LobbyState(s1, ["player1_new"])
    yield from s1.close()
    
@asyncio.coroutine
def FullGameTest():
    s1 = yield from Connect()
    yield from InitialMessage(s1)
    yield from s1.send("name player1")
    yield from LobbyState(s1, ["player1"])
    yield from s1.send("creategame game1 " + GAMETYPE)
    yield from GameWaitStartState(s1, ["player1"])

    s2 = yield from Connect()
    yield from InitialMessage(s2)
    yield from s2.send("name player2")
    yield from LobbyState(s2, ["player2"], ["game1"])
    yield from s2.send("join game1")
    yield from GameWaitStartState(s1, ["player1", "player2"])
    yield from GameWaitStartState(s2, ["player1", "player2"])

    s3 = yield from Connect()
    yield from InitialMessage(s3)
    yield from s3.send("name player3")
    yield from LobbyState(s3, ["player3"], ["game1"])
    yield from s3.send("join game1")
    
    yield from GameState(s1, "Trade", 0, speaker=1,
                         card0="Qd Qh Ks Kc Kd Kh As Ac Ad Ah", \
                         card1="*10", \
                         card2="*10", 
                         cardbuy="*2")
    yield from GameState(s2, "Trade", 1, speaker=1, \
                         card0="*10", 
                         card1="Ts Tc Td Th Js Jc Jd Jh Qs Qc", \
                         card2="*10", \
                         cardbuy="*2")
    yield from GameState(s3, "Trade", 2, speaker=1, \
                         card0="*10", \
                         card1="*10", \
                         card2="7d 7h 8s 8c 8d 8h 9s 9c 9d 9h", \
                         cardbuy="*2")
    
    yield from s1.send("pass")
    yield from GameState(s1, "Trade", 0, speaker=1,
                         card0="Qd Qh Ks Kc Kd Kh As Ac Ad Ah", \
                         card1="*10", \
                         card2="*10", 
                         cardbuy="*2",
                         choice=["pass", None, None])
    yield from GameState(s2, "Trade", 1, speaker=1, \
                         card0="*10", 
                         card1="Ts Tc Td Th Js Jc Jd Jh Qs Qc", \
                         card2="*10", \
                         cardbuy="*2",
                         choice=["pass", None, None])
    yield from GameState(s3, "Trade", 2, speaker=1, \
                         card0="*10", \
                         card1="*10", \
                         card2="7d 7h 8s 8c 8d 8h 9s 9c 9d 9h", \
                         cardbuy="*2",
                         choice=["pass", None, None])
    
    yield from s1.send("pass")
    yield from DontReceive(s2)
    
    yield from s3.send("order game")
    yield from DontReceive(s2)
    
    yield from s3.send("pass")
    yield from GameState(s1, "Trade", 0, speaker=1,
                         card0="Qd Qh Ks Kc Kd Kh As Ac Ad Ah", \
                         card1="*10", \
                         card2="*10", 
                         cardbuy="*2",
                         choice=["pass", None, "pass"])
    yield from GameState(s2, "Trade", 1, speaker=1, \
                         card0="*10", 
                         card1="Ts Tc Td Th Js Jc Jd Jh Qs Qc", \
                         card2="*10", \
                         cardbuy="*2",
                         choice=["pass", None, "pass"])
    yield from GameState(s3, "Trade", 2, speaker=1, \
                         card0="*10", \
                         card1="*10", \
                         card2="7d 7h 8s 8c 8d 8h 9s 9c 9d 9h", \
                         cardbuy="*2",
                         choice=["pass", None, "pass"])
    
    yield from s3.send("order game")
    yield from DontReceive(s2)
    
    yield from s2.send("order game")
    yield from GameState(s1, "WaitDiscard", 0, speaker=1,
                         card0="Qd Qh Ks Kc Kd Kh As Ac Ad Ah", \
                         card1="*12", \
                         card2="*10", 
                         cardbuy="7s 7c",
                         choice=["pass", "game", "pass"])
    yield from GameState(s2, "WaitDiscard", 1, speaker=1, \
                         card0="*10", 
                         card1="Ts Tc Td Th Js Jc Jd Jh Qs Qc 7s 7c", \
                         card2="*10", \
                         cardbuy="7s 7c",
                         choice=["pass", "game", "pass"])
    yield from GameState(s3, "WaitDiscard", 2, speaker=1, \
                         card0="*10", \
                         card1="*12", \
                         card2="7d 7h 8s 8c 8d 8h 9s 9c 9d 9h", \
                         cardbuy="7s 7c",
                         choice=["pass", "game", "pass"])
    
    yield from s2.send("confirm misere 7s 7c")
    yield from DontReceive(s1)
    
    yield from s2.send("confirm 6s 7s 7d")
    yield from DontReceive(s1)
    
    yield from s2.send("confirm 6s 7s 7c")
    yield from GameState(s1, "WaitVist", 0, speaker=2,
                         card0="Qd Qh Ks Kc Kd Kh As Ac Ad Ah", \
                         card1="*10", \
                         card2="*10", \
                         choice=[None, "6s", None], \
                         ready=[0, None, 0])
    yield from GameState(s2, "WaitVist", 1, speaker=2,
                         card0="*10", 
                         card1="Ts Tc Td Th Js Jc Jd Jh Qs Qc", \
                         card2="*10", \
                         choice=[None, "6s", None], \
                         ready=[0, None, 0])
    yield from GameState(s3, "WaitVist", 2, speaker=2, \
                         card0="*10", \
                         card1="*10", \
                         card2="7d 7h 8s 8c 8d 8h 9s 9c 9d 9h", \
                         choice=[None, "6s", None], \
                         ready=[0, None, 0])
    
    yield from s2.send("ready")
    yield from DontReceive(s1)
    
    yield from s1.send("ready")
    yield from GameState(s2, "WaitVist", 1, speaker=2,
                         card0="*10", 
                         card1="Ts Tc Td Th Js Jc Jd Jh Qs Qc", \
                         card2="*10", \
                         choice=[None, "6s", None], \
                         ready=[1, None, 0])
    yield from Recv(s1)
    yield from Recv(s3)

    yield from s1.send("notready")
    yield from GameState(s2, "WaitVist", 1, speaker=2,
                         card0="*10", 
                         card1="Ts Tc Td Th Js Jc Jd Jh Qs Qc", \
                         card2="*10", \
                         choice=[None, "6s", None], \
                         ready=[0, None, 0])
    yield from Recv(s1)
    yield from Recv(s3)

    yield from s3.send("ready")
    yield from GameState(s2, "WaitVist", 1, speaker=2,
                         card0="*10", 
                         card1="Ts Tc Td Th Js Jc Jd Jh Qs Qc", \
                         card2="*10", \
                         choice=[None, "6s", None], \
                         ready=[0, None, 1])
    yield from Recv(s1)
    yield from Recv(s3)

    yield from s1.send("ready")
    yield from GameState(s1, "WaitMove", 0, \
                         card0="Qd Qh Ks Kc Kd Kh As Ac Ad Ah", \
                         card1="*10", \
                         card2="*10", \
                         choice=[None, "6s", None], \
                         tomove=1, \
                         takes=[0, 0, 0])
    yield from GameState(s2, "WaitMove", 1, \
                         card0="*10", 
                         card1="Ts Tc Td Th Js Jc Jd Jh Qs Qc", \
                         card2="*10", \
                         choice=[None, "6s", None], \
                         tomove=1, \
                         takes=[0, 0, 0])
    yield from GameState(s3, "WaitMove", 2, \
                         card0="*10", \
                         card1="*10", \
                         card2="7d 7h 8s 8c 8d 8h 9s 9c 9d 9h", \
                         choice=[None, "6s", None], \
                         tomove=1, \
                         takes=[0, 0, 0])
    
    yield from s1.send("move As")
    yield from DontReceive(s2)
    
    yield from s2.send("move Qc")
    yield from GameState(s1, "WaitMove", 0, \
                         card0="Qd Qh Ks Kc Kd Kh As Ac Ad Ah", \
                         card1="*9", \
                         card2="*10", \
                         choice=[None, "6s", None], \
                         tomove=2, \
                         move=[None, "Qc", None], \
                         takes=[0, 0, 0])
    yield from GameState(s2, "WaitMove", 1, \
                         card0="*10", 
                         card1="Ts Tc Td Th Js Jc Jd Jh Qs", \
                         card2="*10", \
                         choice=[None, "6s", None], \
                         tomove=2, \
                         move=[None, "Qc", None], \
                         takes=[0, 0, 0])
    yield from GameState(s3, "WaitMove", 2, \
                         card0="*10", \
                         card1="*9", \
                         card2="7d 7h 8s 8c 8d 8h 9s 9c 9d 9h", \
                         choice=[None, "6s", None], \
                         tomove=2, \
                         move=[None, "Qc", None], \
                         takes=[0, 0, 0])
    
    yield from s3.send("move 9c")
    yield from GameState(s1, "WaitMove", 0, \
                         card0="Qd Qh Ks Kc Kd Kh As Ac Ad Ah", \
                         card1="*9", \
                         card2="*9", \
                         choice=[None, "6s", None], \
                         tomove=0, \
                         move=[None, "Qc", "9c"], \
                         takes=[0, 0, 0])
    yield from GameState(s2, "WaitMove", 1, \
                         card0="*10", 
                         card1="Ts Tc Td Th Js Jc Jd Jh Qs", \
                         card2="*9", \
                         choice=[None, "6s", None], \
                         tomove=0, \
                         move=[None, "Qc", "9c"], \
                         takes=[0, 0, 0])
    yield from GameState(s3, "WaitMove", 2, \
                         card0="*10", \
                         card1="*9", \
                         card2="7d 7h 8s 8c 8d 8h 9s 9d 9h", \
                         choice=[None, "6s", None], \
                         tomove=0, \
                         move=[None, "Qc", "9c"], \
                         takes=[0, 0, 0])
    
    yield from s1.send("move Ac")
    yield from GameState(s1, "WaitMove", 0, \
                         card0="Qd Qh Ks Kc Kd Kh As Ad Ah", \
                         card1="*9", \
                         card2="*9", \
                         choice=[None, "6s", None], \
                         tomove=0, \
                         move=["Ac", "Qc", "9c"], \
                         takes=[1, 0, 0])
    yield from GameState(s2, "WaitMove", 1, \
                         card0="*9", 
                         card1="Ts Tc Td Th Js Jc Jd Jh Qs", \
                         card2="*9", \
                         choice=[None, "6s", None], \
                         tomove=0, \
                         move=["Ac", "Qc", "9c"], \
                         takes=[1, 0, 0])
    yield from GameState(s3, "WaitMove", 2, \
                         card0="*9", \
                         card1="*9", \
                         card2="7d 7h 8s 8c 8d 8h 9s 9d 9h", \
                         choice=[None, "6s", None], \
                         tomove=0, \
                         move=["Ac", "Qc", "9c"], \
                         takes=[1, 0, 0])
    
    yield from s1.send("move Ad")
    yield from Recv(s1)
    yield from Recv(s2)
    yield from Recv(s3)
    
    yield from s2.send("move Td")
    yield from Recv(s1)
    yield from Recv(s2)
    yield from Recv(s3)
    
    yield from s3.send("move 9d")
    yield from Recv(s1)
    yield from Recv(s2)
    yield from GameState(s3, "WaitMove", 2, \
                         card0="*8", \
                         card1="*8", \
                         card2="7d 7h 8s 8c 8d 8h 9s 9h", \
                         choice=[None, "6s", None], \
                         tomove=0, \
                         move=["Ad", "Td", "9d"], \
                         takes=[2, 0, 0])

    yield from s1.send("move Kd")
    yield from Recv(s1)
    yield from Recv(s2)
    yield from Recv(s3)
    
    yield from s2.send("move Jd")
    yield from Recv(s1)
    yield from Recv(s2)
    yield from Recv(s3)
    
    yield from s3.send("move 8d")
    yield from Recv(s1)
    yield from Recv(s2)
    yield from GameState(s3, "WaitMove", 2, \
                         card0="*7", \
                         card1="*7", \
                         card2="7d 7h 8s 8c 8h 9s 9h", \
                         choice=[None, "6s", None], \
                         tomove=0, \
                         move=["Kd", "Jd", "8d"], \
                         takes=[3, 0, 0])

    yield from s1.send("move Qd")
    yield from Recv(s1)
    yield from Recv(s2)
    yield from Recv(s3)
    
    yield from s2.send("move Qs")
    yield from Recv(s1)
    yield from Recv(s2)
    yield from Recv(s3)
    
    yield from s3.send("move 7d")
    yield from Recv(s1)
    yield from Recv(s2)
    yield from GameState(s3, "WaitMove", 2, \
                         card0="*6", \
                         card1="*6", \
                         card2="7h 8s 8c 8h 9s 9h", \
                         choice=[None, "6s", None], \
                         tomove=1, \
                         move=["Qd", "Qs", "7d"], \
                         takes=[3, 1, 0])

    yield from s2.send("move Jh")
    yield from Recv(s1)
    yield from Recv(s2)
    yield from Recv(s3)
    
    yield from s3.send("move 9h")
    yield from Recv(s1)
    yield from Recv(s2)
    yield from Recv(s3)
    
    yield from s1.send("move Ah")
    yield from Recv(s1)
    yield from Recv(s2)
    yield from GameState(s3, "WaitMove", 2, \
                         card0="*5", \
                         card1="*5", \
                         card2="7h 8s 8c 8h 9s", \
                         choice=[None, "6s", None], \
                         tomove=0, \
                         move=["Ah", "Jh", "9h"], \
                         takes=[4, 1, 0])

    yield from s1.send("move Kh")
    yield from Recv(s1)
    yield from Recv(s2)
    yield from Recv(s3)
    
    yield from s2.send("move Th")
    yield from Recv(s1)
    yield from Recv(s2)
    yield from Recv(s3)
    
    yield from s3.send("move 7h")
    yield from Recv(s1)
    yield from Recv(s2)
    yield from GameState(s3, "WaitMove", 2, \
                         card0="*4", \
                         card1="*4", \
                         card2="8s 8c 8h 9s", \
                         choice=[None, "6s", None], \
                         tomove=0, \
                         move=["Kh", "Th", "7h"], \
                         takes=[5, 1, 0])

    yield from s1.send("move Kc")
    yield from Recv(s1)
    yield from Recv(s2)
    yield from Recv(s3)
    
    yield from s2.send("move Jc")
    yield from Recv(s1)
    yield from Recv(s2)
    yield from Recv(s3)
    
    yield from s3.send("move 8c")
    yield from Recv(s1)
    yield from Recv(s2)
    yield from GameState(s3, "WaitMove", 2, \
                         card0="*3", \
                         card1="*3", \
                         card2="8s 8h 9s", \
                         choice=[None, "6s", None], \
                         tomove=0, \
                         move=["Kc", "Jc", "8c"], \
                         takes=[6, 1, 0])

    yield from s1.send("move Qh")
    yield from Recv(s1)
    yield from Recv(s2)
    yield from Recv(s3)
    
    yield from s2.send("move Js")
    yield from Recv(s1)
    yield from Recv(s2)
    yield from Recv(s3)
    
    yield from s3.send("move 8h")
    yield from Recv(s1)
    yield from Recv(s2)
    yield from GameState(s3, "WaitMove", 2, \
                         card0="*2", \
                         card1="*2", \
                         card2="8s 9s", \
                         choice=[None, "6s", None], \
                         tomove=1, \
                         move=["Qh", "Js", "8h"], \
                         takes=[6, 2, 0])

    yield from s2.send("move Tc")
    yield from Recv(s1)
    yield from Recv(s2)
    yield from Recv(s3)
    
    yield from s3.send("move 8s")
    yield from Recv(s1)
    yield from Recv(s2)
    yield from Recv(s3)
    
    yield from s1.send("move Ks")
    yield from Recv(s1)
    yield from Recv(s2)
    yield from GameState(s3, "WaitMove", 2, \
                         card0="*1", \
                         card1="*1", \
                         card2="9s", \
                         choice=[None, "6s", None], \
                         tomove=0, \
                         move=["Ks", "Tc", "8s"], \
                         takes=[7, 2, 0])

    yield from s1.send("move As")
    yield from Recv(s1)
    yield from Recv(s2)
    yield from Recv(s3)
    
    yield from s2.send("move Ts")
    yield from Recv(s1)
    yield from Recv(s2)
    yield from Recv(s3)
    
    yield from s3.send("move 9s")
    yield from Recv(s1)
    yield from Recv(s2)
    yield from GameState(s3, "WaitRoundStart", 2, \
                         card0=None, \
                         card1=None, \
                         card2=None, \
                         choice=[None, "6s", None], \
                         move=["As", "Ts", "9s"], \
                         takes=[8, 2, 0],
                         ready=[0, 0, 0])
    
    yield from s1.send("ready")
    yield from Recv(s1)
    yield from Recv(s2)
    yield from GameState(s3, "WaitRoundStart", 2, \
                         card0=None, \
                         card1=None, \
                         card2=None, \
                         choice=[None, "6s", None], \
                         move=["As", "Ts", "9s"], \
                         takes=[8, 2, 0],
                         ready=[1, 0, 0])
    
    yield from s2.send("ready")
    yield from Recv(s1)
    yield from Recv(s2)
    yield from GameState(s3, "WaitRoundStart", 2, \
                         card0=None, \
                         card1=None, \
                         card2=None, \
                         choice=[None, "6s", None], \
                         move=["As", "Ts", "9s"], \
                         takes=[8, 2, 0],
                         ready=[1, 1, 0])
    
    
    yield from s3.send("ready")
    yield from Recv(s1)
    yield from Recv(s2)
    yield from GameState(s3, "Trade", 2, speaker=2, \
                         card0="*10", \
                         card1="*10", \
                         card2="7d 7h 8s 8c 8d 8h 9s 9c 9d 9h", \
                         cardbuy="*2")
    
    yield from s1.close()
    yield from s2.close()
    yield from s3.close()

@asyncio.coroutine
def EarlyFinishTest():
    s1 = yield from Connect()
    yield from InitialMessage(s1)
    yield from s1.send("name player1")
    yield from LobbyState(s1, ["player1"])
    yield from s1.send("creategame game1 " + GAMETYPE)
    yield from GameWaitStartState(s1, ["player1"])

    s2 = yield from Connect()
    yield from InitialMessage(s2)
    yield from s2.send("name player2")
    yield from LobbyState(s2, ["player2"], ["game1"])
    yield from s2.send("join game1")
    yield from GameWaitStartState(s1, ["player1", "player2"])
    yield from GameWaitStartState(s2, ["player1", "player2"])

    s3 = yield from Connect()
    yield from InitialMessage(s3)
    yield from s3.send("name player3")
    yield from LobbyState(s3, ["player3"], ["game1"])
    yield from s3.send("join game1")
    yield from Recv(s1)
    yield from Recv(s2)
    yield from Recv(s3)
    
    yield from s1.send("pass")
    yield from Recv(s1)
    yield from Recv(s2)
    yield from Recv(s3)
    
    yield from s3.send("pass")
    yield from Recv(s1)
    yield from Recv(s2)
    yield from Recv(s3)
    
    yield from s2.send("order game")
    yield from Recv(s1)
    yield from Recv(s2)
    yield from Recv(s3)
    
    yield from s1.send("open")
    yield from DontReceive(s2)
    yield from s1.send("close")
    yield from DontReceive(s2)

    yield from s2.send("open")
    yield from GameState(s1, "WaitDiscard", 0, speaker=1,
                         card0="Qd Qh Ks Kc Kd Kh As Ac Ad Ah", \
                         card1="Ts Tc Td Th Js Jc Jd Jh Qs Qc 7s 7c", \
                         card2="*10", 
                         cardbuy="7s 7c",
                         choice=["pass", "game", "pass"])
    yield from GameState(s2, "WaitDiscard", 1, speaker=1, \
                         card0="*10", 
                         card1="Ts Tc Td Th Js Jc Jd Jh Qs Qc 7s 7c", \
                         card2="*10", \
                         cardbuy="7s 7c",
                         choice=["pass", "game", "pass"])
    yield from GameState(s3, "WaitDiscard", 2, speaker=1, \
                         card0="*10", \
                         card1="Ts Tc Td Th Js Jc Jd Jh Qs Qc 7s 7c", \
                         card2="7d 7h 8s 8c 8d 8h 9s 9c 9d 9h", \
                         cardbuy="7s 7c",
                         choice=["pass", "game", "pass"])
    
    yield from s2.send("close")
    yield from GameState(s1, "WaitDiscard", 0, speaker=1,
                         card0="Qd Qh Ks Kc Kd Kh As Ac Ad Ah", \
                         card1="*12", \
                         card2="*10", 
                         cardbuy="7s 7c",
                         choice=["pass", "game", "pass"])
    yield from GameState(s2, "WaitDiscard", 1, speaker=1, \
                         card0="*10", 
                         card1="Ts Tc Td Th Js Jc Jd Jh Qs Qc 7s 7c", \
                         card2="*10", \
                         cardbuy="7s 7c",
                         choice=["pass", "game", "pass"])
    yield from GameState(s3, "WaitDiscard", 2, speaker=1, \
                         card0="*10", \
                         card1="*12", \
                         card2="7d 7h 8s 8c 8d 8h 9s 9c 9d 9h", \
                         cardbuy="7s 7c",
                         choice=["pass", "game", "pass"])
    
    yield from s2.send("confirm 6s 7s 7c")
    yield from Recv(s1)
    yield from Recv(s2)
    yield from Recv(s3)
    
    yield from s1.send("ready")
    yield from Recv(s1)
    yield from Recv(s2)
    yield from Recv(s3)

    yield from s3.send("ready")
    yield from Recv(s1)
    yield from Recv(s2)
    yield from Recv(s3)

    yield from s1.send("open")
    yield from GameState(s1, "WaitMove", 0, \
                         card0="Qd Qh Ks Kc Kd Kh As Ac Ad Ah", \
                         card1="*10", \
                         card2="*10", \
                         choice=[None, "6s", None], \
                         tomove=1, \
                         takes=[0, 0, 0])
    yield from GameState(s2, "WaitMove", 1, \
                         card0="Qd Qh Ks Kc Kd Kh As Ac Ad Ah", 
                         card1="Ts Tc Td Th Js Jc Jd Jh Qs Qc", \
                         card2="*10", \
                         choice=[None, "6s", None], \
                         tomove=1, \
                         takes=[0, 0, 0])
    yield from GameState(s3, "WaitMove", 2, \
                         card0="Qd Qh Ks Kc Kd Kh As Ac Ad Ah", \
                         card1="*10", \
                         card2="7d 7h 8s 8c 8d 8h 9s 9c 9d 9h", \
                         choice=[None, "6s", None], \
                         tomove=1, \
                         takes=[0, 0, 0])

    yield from s3.send("open")
    yield from GameState(s1, "WaitMove", 0, \
                         card0="Qd Qh Ks Kc Kd Kh As Ac Ad Ah", \
                         card1="*10", \
                         card2="7d 7h 8s 8c 8d 8h 9s 9c 9d 9h", \
                         choice=[None, "6s", None], \
                         tomove=1, \
                         takes=[0, 0, 0])
    yield from GameState(s2, "WaitMove", 1, \
                         card0="Qd Qh Ks Kc Kd Kh As Ac Ad Ah", 
                         card1="Ts Tc Td Th Js Jc Jd Jh Qs Qc", \
                         card2="7d 7h 8s 8c 8d 8h 9s 9c 9d 9h", \
                         choice=[None, "6s", None], \
                         tomove=1, \
                         takes=[0, 0, 0])
    yield from GameState(s3, "WaitMove", 2, \
                         card0="Qd Qh Ks Kc Kd Kh As Ac Ad Ah", \
                         card1="*10", \
                         card2="7d 7h 8s 8c 8d 8h 9s 9c 9d 9h", \
                         choice=[None, "6s", None], \
                         tomove=1, \
                         takes=[0, 0, 0])

    yield from s2.send("finish")
    yield from GameState(s1, "WaitMove", 0, \
                         card0="Qd Qh Ks Kc Kd Kh As Ac Ad Ah", \
                         card1="*10", \
                         card2="7d 7h 8s 8c 8d 8h 9s 9c 9d 9h", \
                         choice=[None, "6s", None], \
                         tomove=1, \
                         takes=[0, 0, 0], \
                         wantsFinish="1")
    yield from GameState(s2, "WaitMove", 1, \
                         card0="Qd Qh Ks Kc Kd Kh As Ac Ad Ah", 
                         card1="Ts Tc Td Th Js Jc Jd Jh Qs Qc", \
                         card2="7d 7h 8s 8c 8d 8h 9s 9c 9d 9h", \
                         choice=[None, "6s", None], \
                         tomove=1, \
                         takes=[0, 0, 0], \
                         wantsFinish="1")
    yield from GameState(s3, "WaitMove", 2, \
                         card0="Qd Qh Ks Kc Kd Kh As Ac Ad Ah", \
                         card1="*10", \
                         card2="7d 7h 8s 8c 8d 8h 9s 9c 9d 9h", \
                         choice=[None, "6s", None], \
                         tomove=1, \
                         takes=[0, 0, 0], \
                         wantsFinish="1")
    
    yield from s3.send("finish")
    yield from GameState(s1, "WaitMove", 0, \
                         card0="Qd Qh Ks Kc Kd Kh As Ac Ad Ah", \
                         card1="*10", \
                         card2="7d 7h 8s 8c 8d 8h 9s 9c 9d 9h", \
                         choice=[None, "6s", None], \
                         tomove=1, \
                         takes=[0, 0, 0], \
                         wantsFinish="1 2")
    yield from GameState(s2, "WaitMove", 1, \
                         card0="Qd Qh Ks Kc Kd Kh As Ac Ad Ah", 
                         card1="Ts Tc Td Th Js Jc Jd Jh Qs Qc", \
                         card2="7d 7h 8s 8c 8d 8h 9s 9c 9d 9h", \
                         choice=[None, "6s", None], \
                         tomove=1, \
                         takes=[0, 0, 0], \
                         wantsFinish="1 2")
    yield from GameState(s3, "WaitMove", 2, \
                         card0="Qd Qh Ks Kc Kd Kh As Ac Ad Ah", \
                         card1="*10", \
                         card2="7d 7h 8s 8c 8d 8h 9s 9c 9d 9h", \
                         choice=[None, "6s", None], \
                         tomove=1, \
                         takes=[0, 0, 0], \
                         wantsFinish="1 2")
    
    yield from s1.send("finish")
    yield from Recv(s1)
    yield from Recv(s2)
    yield from GameState(s3, "WaitRoundStart", 2, \
                         card0=None, \
                         card1=None, \
                         card2=None, \
                         choice=[None, "6s", None], \
                         takes=[0, 0, 0],
                         ready=[0, 0, 0])
    
    yield from s1.close()
    yield from s2.close()
    yield from s3.close()

@asyncio.coroutine
def ShareCardsTest():
    s1 = yield from Connect()
    yield from InitialMessage(s1)
    yield from s1.send("name player1")
    yield from LobbyState(s1, ["player1"])
    yield from s1.send("creategame game1 " + GAMETYPE)
    yield from GameWaitStartState(s1, ["player1"])

    s2 = yield from Connect()
    yield from InitialMessage(s2)
    yield from s2.send("name player2")
    yield from LobbyState(s2, ["player2"], ["game1"])
    yield from s2.send("join game1")
    yield from GameWaitStartState(s1, ["player1", "player2"])
    yield from GameWaitStartState(s2, ["player1", "player2"])

    s3 = yield from Connect()
    yield from InitialMessage(s3)
    yield from s3.send("name player3")
    yield from LobbyState(s3, ["player3"], ["game1"])
    yield from s3.send("join game1")
    yield from Recv(s1)
    yield from Recv(s2)
    yield from Recv(s3)
    
    yield from s1.send("pass")
    yield from Recv(s1)
    yield from Recv(s2)
    yield from Recv(s3)
    
    yield from s2.send("pass")
    yield from Recv(s1)
    yield from Recv(s2)
    yield from Recv(s3)
    
    yield from s3.send("order game")
    yield from Recv(s1)
    yield from Recv(s2)
    yield from Recv(s3)
    
    yield from s3.send("confirm 6s 7s 7c")
    yield from Recv(s1)
    yield from Recv(s2)
    yield from Recv(s3)
    
    yield from s1.send("ready")
    yield from Recv(s1)
    yield from Recv(s2)
    yield from Recv(s3)

    yield from s2.send("ready")
    yield from Recv(s1)
    yield from Recv(s2)
    yield from Recv(s3)
    
    yield from s1.send("share")
    yield from DontReceive(s3)
    
    yield from s1.send("open")
    yield from Recv(s1)
    yield from Recv(s2)
    yield from Recv(s3)
    
    yield from s1.send("share")
    yield from Recv(s1)
    yield from Recv(s3)
    yield from GameState(s2, "WaitMove", 1, \
                         card0="Qd Qh Ks Kc Kd Kh As Ac Ad Ah", \
                         card1="Ts Tc Td Th Js Jc Jd Jh Qs Qc", \
                         card2="*10", \
                         choice=[None, None, "6s"], \
                         tomove=1, \
                         takes=[0, 0, 0], \
                         shares=[1, None, None])

    yield from s2.send("share")
    yield from DontReceive(s1)
    
    yield from s2.send("open")
    yield from Recv(s1)
    yield from Recv(s2)
    yield from Recv(s3)

    yield from s3.send("open")
    yield from Recv(s1)
    yield from Recv(s2)
    yield from Recv(s3)

    yield from s3.send("share")
    yield from DontReceive(s1)
    
    yield from s1.send("movefor 1 Ts")
    yield from DontReceive(s1)

    yield from s2.send("share")
    yield from GameState(s1, "WaitMove", 0, \
                         card0="Qd Qh Ks Kc Kd Kh As Ac Ad Ah", \
                         card1="Ts Tc Td Th Js Jc Jd Jh Qs Qc", \
                         card2="7d 7h 8s 8c 8d 8h 9s 9c 9d 9h", \
                         choice=[None, None, "6s"], \
                         tomove=1, \
                         takes=[0, 0, 0], \
                         shares=[1, 0, None])
    yield from Recv(s2)
    yield from Recv(s3)
    
    yield from s1.send("movefor 1 Ts")
    yield from GameState(s1, "WaitMove", 0, \
                         card0="Qd Qh Ks Kc Kd Kh As Ac Ad Ah", \
                         card1="Tc Td Th Js Jc Jd Jh Qs Qc", \
                         card2="7d 7h 8s 8c 8d 8h 9s 9c 9d 9h", \
                         choice=[None, None, "6s"], \
                         tomove=2, \
                         move=[None, "Ts", None], \
                         takes=[0, 0, 0], \
                         shares=[1, 0, None])
    yield from Recv(s2)
    yield from Recv(s3)

    
    yield from s1.close()
    yield from s2.close()
    yield from s3.close()

@asyncio.coroutine
def ScoreTest():
    s1 = yield from Connect()
    yield from InitialMessage(s1)
    yield from s1.send("editscore p0 20");
    yield from s1.send("name player1")
    yield from LobbyState(s1, ["player1"])
    yield from s1.send("editscore p0 20");
    yield from s1.send("creategame game1 " + GAMETYPE)
    yield from GameWaitStartState(s1, ["player1"])
    yield from s1.send("editscore p0 20");

    s2 = yield from Connect()
    yield from InitialMessage(s2)
    yield from s2.send("editscore p0 20");
    yield from s2.send("name player2")
    yield from LobbyState(s2, ["player2"], ["game1"])
    yield from s2.send("editscore p0 20");
    yield from s2.send("join game1")
    yield from GameWaitStartState(s1, ["player1", "player2"])
    yield from GameWaitStartState(s2, ["player1", "player2"])
    yield from s2.send("editscore p0 20");

    s3 = yield from Connect()
    yield from InitialMessage(s3)
    yield from s3.send("editscore p0 20");
    yield from s3.send("name player3")
    yield from LobbyState(s3, ["player3"], ["game1"])
    yield from s3.send("editscore p0 20");
    yield from s3.send("join game1")
    yield from Recv(s1)
    yield from Recv(s2)
    yield from Recv(s3)

    yield from s1.send("editscore p0 1");
    yield from GameStartState(s1, s2, s3, p=[1, 0, 0])
    yield from s2.send("editscore p1 2");
    yield from GameStartState(s1, s2, s3, p=[1, 2, 0])
    yield from s3.send("editscore p2 3");
    yield from GameStartState(s1, s2, s3, p=[1, 2, 3])

    yield from s1.send("editscore g0 10");
    yield from GameStartState(s1, s2, s3, p=[1, 2, 3], g = [10, 0, 0])
    yield from s2.send("editscore g1 20");
    yield from GameStartState(s1, s2, s3, p=[1, 2, 3], g = [10, 20, 0])
    yield from s3.send("editscore g2 30");
    yield from GameStartState(s1, s2, s3, p=[1, 2, 3], g = [10, 20, 30])

    yield from s1.send("editscore v01 101");
    yield from GameStartState(s1, s2, s3, p=[1, 2, 3], g = [10, 20, 30], v = [101, 0, 0, 0, 0, 0])
    yield from s1.send("editscore v02 102");
    yield from GameStartState(s1, s2, s3, p=[1, 2, 3], g = [10, 20, 30], v = [101, 102, 0, 0, 0, 0])
    yield from s1.send("editscore v10 110");
    yield from GameStartState(s1, s2, s3, p=[1, 2, 3], g = [10, 20, 30], v = [101, 102, 110, 0, 0, 0])
    yield from s1.send("editscore v12 112");
    yield from GameStartState(s1, s2, s3, p=[1, 2, 3], g = [10, 20, 30], v = [101, 102, 110, 112, 0, 0])
    yield from s1.send("editscore v20 120");
    yield from GameStartState(s1, s2, s3, p=[1, 2, 3], g = [10, 20, 30], v = [101, 102, 110, 112, 120, 0])
    yield from s1.send("editscore v21 121");
    yield from GameStartState(s1, s2, s3, p=[1, 2, 3], g = [10, 20, 30], v = [101, 102, 110, 112, 120, 121])

    yield from s1.send("editscore p0 1");
    yield from s2.send("editscore p1 2");
    yield from s3.send("editscore p2 3");
    yield from s1.send("editscore g0 10");
    yield from s2.send("editscore g1 20");
    yield from s3.send("editscore g2 30");
    yield from s1.send("editscore v01 101");
    yield from s1.send("editscore v02 102");
    yield from s1.send("editscore v10 110");
    yield from s1.send("editscore v12 112");
    yield from s1.send("editscore v20 120");
    yield from s1.send("editscore v21 121");

    yield from s1.send("editscore x 4");
    yield from s1.send("editscore p3 4");
    yield from s1.send("editscore g3 4");
    yield from s1.send("editscore v00 4");
    yield from s1.send("editscore v11 4");
    yield from s1.send("editscore v22 4");
    yield from s1.send("editscore v03 4");
    yield from s1.send("editscore v13 4");
    yield from s1.send("editscore v23 4");
    yield from s1.send("editscore v30 4");
    yield from DontReceive(s1)
    yield from DontReceive(s2)
    yield from DontReceive(s3)
    
tests = [ \
            CreateGameTest, \
            RepeatNameTest, \
            StartGameTest, \
            FullGameTest, \
            EarlyFinishTest, \
            ShareCardsTest, \
            ScoreTest
        ]
    
complete=0
for test in tests:
    asyncio.get_event_loop().run_until_complete(test())
    complete += 1

print(complete, "tests completed successfully")
