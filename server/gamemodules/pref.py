import cardgame
import random
from games import DecodeArgs
import functools

class PrefDeck(cardgame.Deck):
    def __init__(this):
        cardgame.Deck.__init__(this, [cardgame.MakeCard(value, suit) \
            for value in [cardgame.CARD_7, cardgame.CARD_8, cardgame.CARD_9, cardgame.CARD_10, \
                          cardgame.CARD_J, cardgame.CARD_Q, cardgame.CARD_K, cardgame.CARD_A] \
            for suit in [cardgame.SUIT_SPADE, cardgame.SUIT_CLUB, \
                         cardgame.SUIT_DIAMOND, cardgame.SUIT_HEART]])

def PoolVar(n):
    return "p"+str(n)

def PenaltyVar(n):
    return "g"+str(n)

def VistVar(by, on):
    return "v"+str(by)+str(on)

def PlayerCardsVar(n):
    return "cards"+str(n)

def PlayerMoveVar(n):
    return "move"+str(n)

def PlayerChoiceVar(n):
    return "choice"+str(n)

def PlayerShareVar(n):
    return "share"+str(n)

BoughtCardsVar = "buy"

def PlayerReadyVar(n):
    return "ready"+str(n)

def PlayerTakesVar(n):
    return "take"+str(n)

def DecodeOrder(s):
    s = DecodeArgs(s, 1)
    if (s == "game") or (s == "misere"):
        return s
    else:
        return None

def IsSuit(c):
    return (c == cardgame.SUIT_SPADE) or (c == cardgame.SUIT_CLUB) or \
           (c == cardgame.SUIT_DIAMOND) or (c == cardgame.SUIT_HEART)

SUIT_NONE = "n"

def IsValidContract(s):
    if s == "misere":
        return True
    if (len(s) == 2) and ((s[0] == cardgame.CARD_6) or (s[0] == cardgame.CARD_7) or \
                          (s[0] == cardgame.CARD_8) or (s[0] == cardgame.CARD_9) or \
                          (s[0] == cardgame.CARD_10)) and (IsSuit(s[1]) or (s[1] == SUIT_NONE)):
        return True
                         
    return False

def IsValidCard(s):
    if (len(s) == 2) and ((s[0] == cardgame.CARD_7) or (s[0] == cardgame.CARD_8) or \
                          (s[0] == cardgame.CARD_9) or (s[0] == cardgame.CARD_10) or \
                          (s[0] == cardgame.CARD_J) or (s[0] == cardgame.CARD_K) or \
                          (s[0] == cardgame.CARD_Q) or (s[0] == cardgame.CARD_A)) and \
       IsSuit(s[1]):
        return True
                         
    return False

def DecodeOrderConfirmation(s):
    words = DecodeArgs(s, 3)
    if words and IsValidContract(words[0]) and IsValidCard(words[1]) and \
       IsValidCard(words[2]) and (words[1] != words[2]):
        return words
    else:
        return None

def DecodeCard(s):
    card = DecodeArgs(s, 1)
    if card and IsValidCard(card):
        return card
    else:
        return None

def DecodeMoveFor(s):
    words = DecodeArgs(s, 2)
    if words:
        card = words[1]
        try:
            pos = int(words[0])
        except:
            return None
        if (pos > 0) and (pos < 3) and IsValidCard(card):
            return [pos, card]
    return None

def DecodeEditScore(nplayer, s):
    words = DecodeArgs(s, 2)
    try:
        value = int(words[1])
    except:
        return None

    for i in range(nplayer):
        if (words[0] == PoolVar(i)) or (words[0] == PenaltyVar(i)):
            return [words[0], value]
        for j in range(nplayer):
            if (j != i) and (words[0] == VistVar(i, j)):
                return [words[0], value]

    return None

values = {cardgame.CARD_7: 7, cardgame.CARD_8: 8, cardgame.CARD_9: 9, cardgame.CARD_10: 10, \
          cardgame.CARD_J: 11, cardgame.CARD_Q: 12, cardgame.CARD_K: 13, cardgame.CARD_A: 14}

def GreaterValue(v1, v2):
    return values[v1] > values[v2]

class Game(cardgame.CardGame):
    def __init__(this, name):
        cardgame.CardGame.__init__(this, name)
        this.shuffleMethod = cardgame.SHUFFLE_RANDOMORDER
        this.deck = PrefDeck()
        this.TotusChecked = True
    
    def GetTypeName(this):
        return "rostov3"
    
    def GetPlayerCount(this):
        return 3
    
    def Create(g):
        g.eStartRound = g.AddEvent()
        g.ePass = g.AddEvent()
        g.eOrder = g.AddEvent()
        g.eConfirmOrder = g.AddEvent()
        g.eVist = g.AddEvent()
        g.eReady = g.AddEvent()
        g.eNotReady = g.AddEvent()
        g.eStartMoves = g.AddEvent()
        g.eMove = g.AddEvent()
        g.eConfirmScore = g.AddEvent()
        g.eOpenCards = g.AddEvent()
        g.eCloseCards = g.AddEvent()
        g.eWantsFinishRound = g.AddEvent()
        g.eShareCards = g.AddEvent()
        g.eMoveFor = g.AddEvent()
        g.eEditScore = g.AddEvent()

        g.stWaitingForRoundStart = g.AddState("WaitRoundStart")
        g.stTrade = g.AddState("Trade")
        g.stWaitingForDiscard = g.AddState("WaitDiscard")
        g.stWaitingForVist = g.AddState("WaitVist")
        g.stWaitingForMove = g.AddState("WaitMove")
        g.stWaitingForScoreConfirm = g.AddState("WaitScoreConfirm")
        
        g.cmdPass = g.AddCommand()
        g.cmdOrder = g.AddCommand()
        g.cmdConfirmOrder = g.AddCommand()
        g.cmdReady = g.AddCommand()
        g.cmdNotReady = g.AddCommand()
        g.cmdMove = g.AddCommand()
        g.cmdMoveFor = g.AddCommand()
        g.cmdOpenCards = g.AddCommand()
        g.cmdCloseCards = g.AddCommand()
        g.cmdWantFinishRound = g.AddCommand()
        g.cmdShareCards = g.AddCommand()
        g.cmdEditScore = g.AddCommand()
        g.DefineCommand("pass", g.cmdPass, lambda x: 0, g.PassCommand)
        g.DefineCommand("order", g.cmdOrder, DecodeOrder, g.OrderCommand)
        g.DefineCommand("confirm", g.cmdConfirmOrder, DecodeOrderConfirmation, g.ConfirmOrderCommand)
        g.DefineCommand("ready", g.cmdReady, lambda x: 0, g.ReadyCommand)
        g.DefineCommand("notready", g.cmdNotReady, lambda x: 0, g.NotReadyCommand)
        g.DefineCommand("move", g.cmdMove, DecodeCard, g.MoveCommand)
        g.DefineCommand("open", g.cmdOpenCards, lambda x: 0, g.OpenCardsCommand)
        g.DefineCommand("close", g.cmdCloseCards, lambda x: 0, g.CloseCardsCommand)
        g.DefineCommand("finish", g.cmdWantFinishRound, lambda x: 0, g.FinishRoundCommand)
        g.DefineCommand("share", g.cmdShareCards, lambda x: 0, g.ShareCardsCommand)
        g.DefineCommand("movefor", g.cmdMoveFor, DecodeMoveFor, g.MoveForCommand)
        g.DefineCommand("editscore", g.cmdEditScore, lambda s: DecodeEditScore(g.GetPlayerCount(), s), g.EditScoreCommand)

        g.Event(g.eStartGame, g.stWaitingForStart, g.StartGame)
        g.Event(g.eStartRound, g.stWaitingForRoundStart, g.StartRound)
        g.Event(g.ePass, g.stTrade, g.PlayerPassTrade)
        g.Event(g.eOrder, g.stTrade, g.Ordered)
        g.Event(g.eStartMoves, g.stTrade, g.StartMoves)
        g.Event(g.eConfirmOrder, g.stWaitingForDiscard, g.OrderConfirmed)
        g.Event(g.eReady, g.stWaitingForVist, g.PlayerVistReady)
        g.Event(g.eNotReady, g.stWaitingForVist, g.PlayerVistNotReady)
        g.Event(g.eStartMoves, g.stWaitingForVist, g.StartMoves)
        g.Event(g.eMove, g.stWaitingForMove, g.MakeMove)
        g.Event(g.eReady, g.stWaitingForRoundStart, g.PlayerRoundStartReady)
        g.Event(g.eNotReady, g.stWaitingForRoundStart, g.PlayerRoundStartNotReady)
        g.Event(g.eOpenCards, g.stWaitingForDiscard, g.OpenPlayerCards)
        g.Event(g.eCloseCards, g.stWaitingForDiscard, g.ClosePlayerCards)
        g.Event(g.eOpenCards, g.stWaitingForMove, g.OpenPlayerCards)
        g.Event(g.eWantsFinishRound, g.stWaitingForMove, g.PlayerWantsFinishRound)
        g.Event(g.eShareCards, g.stWaitingForMove, g.PlayerSharesCards)
        g.Event(g.eMoveFor, g.stWaitingForMove, g.PlayerMovesForAnother)
        g.Event(g.eEditScore, g.stWaitingForRoundStart, g.EditScore)
        g.Event(g.eEditScore, g.stTrade, g.EditScore)
        g.Event(g.eEditScore, g.stWaitingForDiscard, g.EditScore)
        g.Event(g.eEditScore, g.stWaitingForVist, g.EditScore)
        g.Event(g.eEditScore, g.stWaitingForMove, g.EditScore)
        g.Event(g.eEditScore, g.stWaitingForScoreConfirm, g.EditScore)
    
    def ChooseDealer(g):
        return random.randint(0, g.GetPlayerCount()-1)

    def StartGame(g, arg):
        nplayer = g.GetPlayerCount()
        g.SetVar("player0", g.players[0].name)
        g.SetVar("player1", g.players[1].name)
        g.SetVar("player2", g.players[2].name)
        g.nextdealer = g.ChooseDealer()
        g.AddVar("speaker")
        for i in range(nplayer):
            g.SetVar(PoolVar(i), 0)
            g.SetVar(PenaltyVar(i), 0)
            for j in range(nplayer):
                if j != i:
                    g.SetVar(VistVar(i,j), 0)
        for i in range(nplayer):
            g.CreateCardPile(PlayerCardsVar(i))
        for i in range(nplayer):
            g.CreateCardPile(PlayerMoveVar(i))
        g.CreateCardPile(BoughtCardsVar)
        for i in range(nplayer):
            g.AddVar(PlayerChoiceVar(i))
        for i in range(nplayer):
            g.AddVar(PlayerReadyVar(i))
        for i in range(nplayer):
            g.AddVar(PlayerTakesVar(i))
        for i in range(nplayer):
            g.AddVar(PlayerShareVar(i))
        g.AddVar("tomove")
        g.SetState(g.stWaitingForRoundStart)
        g.HandleEvent(g.eStartRound, None)

    def StartRound(g, arg):
        g.deck.Restore()
        g.deck.Shuffle(g.shuffleMethod)
        g.DealToCardPile(g.deck, PlayerCardsVar(0), 10)
        g.DealToCardPile(g.deck, PlayerCardsVar(1), 10)
        g.DealToCardPile(g.deck, PlayerCardsVar(2), 10)
        g.DealToCardPile(g.deck, BoughtCardsVar, 2)
        g.CloseCardPile(BoughtCardsVar)
        g.wantsFinishRound = [False]*g.GetPlayerCount()
        
        for i in range(g.GetPlayerCount()):
            g.SetVar(PlayerTakesVar(i), "")
            g.SetVar(PlayerChoiceVar(i), "")
            g.DiscardCardPile(PlayerMoveVar(i))
            g.CloseCardPile(PlayerCardsVar(i))
            g.OpenCardPile(PlayerCardsVar(i), g.players[i])
            g.SetVar(PlayerShareVar(i), "")

        g.dealer = g.nextdealer
        g.nextdealer = (g.dealer+1) % g.GetPlayerCount()
        g.SetVar("speaker", g.nextdealer)
        g.firstmove = g.nextdealer
        
        g.SetState(g.stTrade)
        g.SendUpdate()
        
    def PassCommand(g, client, arg):
        g.HandleEvent(g.ePass, client.id)
    
    def IsMiracle(g):
        return sum(map(lambda i: 1 if g.GetVar(PlayerChoiceVar(i))=="pass" else 0, range(g.GetPlayerCount()))) == 2
    
    def PlayerPassTrade(g, clientId):
        pos=g.GetPlayerPosition(clientId)
        if g.GetVar(PlayerChoiceVar(pos)) != "":
            print("Player", g.clients[clientId].name, "passes again, ignored")
            return
        
        isPassout = g.IsMiracle()
        g.SetVar(PlayerChoiceVar(pos), "pass")
        if isPassout:
            g.trumpSuit = SUIT_NONE
            g.DiscardCardPile(BoughtCardsVar)
            g.HandleEvent(g.eStartMoves, None)
            return
        g.SendUpdate()
    
    def OrderCommand(g, client, order):
        g.HandleEvent(g.eOrder, [client.id, order])
    
    def Ordered(g, arg):
        [clientId, order] = arg
        playerName = g.clients[clientId].name
        pos=g.GetPlayerPosition(clientId)
        
        if g.GetVar(PlayerChoiceVar(pos)) != "":
            print("Player", playerName, "ordered after pass, ignored")
            return
        
        if not g.IsMiracle():
            print("Player", playerName, "ordered too early, ignored")
            return
        
        g.SetVar(PlayerChoiceVar(pos), order)
        for i in range(g.GetPlayerCount()):
            g.OpenCardPile(BoughtCardsVar, g.players[i])
            if order == "misere":
                g.OpenCardPile(PlayerCardsVar(pos), g.players[i])
        g.SetVar(PlayerCardsVar(pos), g.GetVar(PlayerCardsVar(pos)) + g.GetVar(BoughtCardsVar))
        
        g.SetState(g.stWaitingForDiscard)
        g.SendUpdate()

    def ConfirmOrderCommand(g, client, arg):
        g.HandleEvent(g.eConfirmOrder, [client.id] + arg)
    
    def OrderConfirmed(g, arg):
        [clientId, order, discard1, discard2] = arg
        pos=g.GetPlayerPosition(clientId)
        playerName = g.clients[clientId].name
        
        baseOrder = g.GetVar(PlayerChoiceVar(pos))
        if baseOrder == "pass":
            print("Player", playerName, "confirms order after pass, ignored")
            return
        elif baseOrder == "game":
            if order == "misere":
                print("Player", playerName, "confirms non-misere as misere, ignored")
                return
        elif baseOrder == "misere":
            if order != "misere":
                print("Player", playerName, "confirms misere as something else, ignored")
                return
        
        cards = g.GetVar(PlayerCardsVar(pos))
        if not discard1 in cards or not discard2 in cards:
            print("Player", playerName, "tries to discard card he doesn't have, ignored")
            return

        cards.remove(discard1)
        cards.remove(discard2)
        g.DiscardCardPile(BoughtCardsVar)
        g.SetVar(PlayerChoiceVar(pos), order)
        
        if order == "misere":
            for i in range(g.GetPlayerCount()):
                if i != pos:
                    g.CloseCardPile(PlayerCardsVar(pos), g.players[i])
        
        g.SetVar("speaker", (pos+1) % g.GetPlayerCount())
        for i in range(g.GetPlayerCount()):
            if g.GetVar(PlayerChoiceVar(i)) == "pass":
                g.SetVar(PlayerChoiceVar(i), "")
        
        if order == "misere":
            g.trumpSuit = SUIT_NONE
        else:
            g.trumpSuit = order[1]
        
        g.SetState(g.stWaitingForVist)
        if (order == "misere") or ((order[0] == cardgame.CARD_10) and g.TotusChecked):
            g.HandleEvent(g.eStartMoves, None)
            return
        
        for i in range(g.GetPlayerCount()):
            if i != pos:
                g.SetVar(PlayerReadyVar(i), 0)

        g.SendUpdate()
                
    def ReadyCommand(g, client, arg):
        g.HandleEvent(g.eReady, client.id)
    
    def NotReadyCommand(g, client, arg):
        g.HandleEvent(g.eNotReady, client.id)
    
    def AllReady(g):
        for i in range(g.GetPlayerCount()):
            if g.GetVar(PlayerReadyVar(i)) == 0:
                return False
        return True
    
    def PlayerVistReady(g, clientId):
        pos=g.GetPlayerPosition(clientId)
        playerName = g.clients[clientId].name

        if g.GetVar(PlayerChoiceVar(pos)) != "":
            print("Player", playerName, "ready but he's the one having contract, ignored")
            return
        
        g.SetVar(PlayerReadyVar(pos), 1)
        if g.AllReady():
            for i in range(g.GetPlayerCount()):
                g.SetVar(PlayerReadyVar(i), None)
            g.HandleEvent(g.eStartMoves, None)
            return
        
        g.SendUpdate()

    def PlayerVistNotReady(g, clientId):
        pos=g.GetPlayerPosition(clientId)
        playerName = g.clients[clientId].name

        if g.GetVar(PlayerChoiceVar(pos)) != "":
            print("Player", playerName, "not ready but he's the one having contract, ignored")
            return
        
        g.SetVar(PlayerReadyVar(pos), 0)
        g.SendUpdate()

    def StartMoves(g, arg):
        g.SetVar("tomove", g.firstmove)
        for i in range(g.GetPlayerCount()):
            g.SetVar(PlayerTakesVar(i), 0)
        g.SetVar("speaker", "")
        
        g.SetState(g.stWaitingForMove)
        g.SendUpdate()
        
    def MoveCommand(g, client, card):
        g.HandleEvent(g.eMove, [client.id, card])
    
    def AllMoved(g):
        for i in range(g.GetPlayerCount()):
            if len(g.GetVar(PlayerMoveVar(i))) == 0:
                return False
        return True

    def NobodyMoved(g):
        for i in range(g.GetPlayerCount()):
            if len(g.GetVar(PlayerMoveVar(i))) != 0:
                return False
        return True
    
    def WhoTook(g):
        bestPlayer = 999
        bestCard = None
        for i in range(g.GetPlayerCount()):
            card = g.GetVar(PlayerMoveVar(i))[0]
            if (card[1] != g.moveSuit) and (card[1] != g.trumpSuit):
                continue
            
            if bestCard != None:
                if (bestCard[1] == g.trumpSuit) and (card[1] != g.trumpSuit):
                    continue
                if (bestCard[1] == card[1]) and GreaterValue(bestCard[0], card[0]):
                    continue
            
            bestCard = card
            bestPlayer = i
        return bestPlayer
    
    def FinishRound(g):
        g.SetVar("tomove", None)
        g.SetVar("wantfinish", "")
        for i in range(g.GetPlayerCount()):
            g.DiscardCardPile(PlayerCardsVar(i));
            g.SetVar(PlayerReadyVar(i), 0);
        g.SetState(g.stWaitingForRoundStart)
    
    def MakeMove(g, arg):
        [clientId, card] = arg
        pos = g.GetPlayerPosition(clientId)
        playerName = g.clients[clientId].name
        
        if pos != g.GetVar("tomove"):
            print("Player", playerName, "moves out of turn, ignored")
            return
        
        cards = g.GetVar(PlayerCardsVar(pos))
        if not card in cards:
            print("Player", playerName, "puts a card he doesn't have, ignored")
            return
        
        if g.AllMoved():
            for i in range(g.GetPlayerCount()):
                g.DiscardCardPile(PlayerMoveVar(i))

        if g.NobodyMoved():
            g.moveSuit = card[1]

        cards.remove(card)
        g.AddCardToPile(PlayerMoveVar(pos), card)
        for i in range(g.GetPlayerCount()):
            g.OpenCardPile(PlayerMoveVar(pos), g.players[i])
        if g.AllMoved():
            whotook = g.WhoTook()
            g.SetVar(PlayerTakesVar(whotook), g.GetVar(PlayerTakesVar(whotook))+1)
            if len(cards) == 0:
                g.FinishRound()
            else:
                g.SetVar("tomove", whotook)
        else:
            g.SetVar("tomove", (g.GetVar("tomove")+1) % g.GetPlayerCount())
            
        g.SendUpdate()
    
    def PlayerRoundStartReady(g, clientId):
        pos = g.GetPlayerPosition(clientId)

        g.SetVar(PlayerReadyVar(pos), 1)
        if g.AllReady():
            for i in range(g.GetPlayerCount()):
                g.SetVar(PlayerReadyVar(i), None)
            g.HandleEvent(g.eStartRound, None)
            return
        
        g.SendUpdate()

    def PlayerRoundStartNotReady(g, clientId):
        pos = g.GetPlayerPosition(clientId)
        
        g.SetVar(PlayerReadyVar(pos), 0)
        g.SendUpdate()

    def OpenCardsCommand(g, client, arg):
        g.HandleEvent(g.eOpenCards, client.id)
    
    def CloseCardsCommand(g, client, arg):
        g.HandleEvent(g.eCloseCards, client.id)
    
    def OpenPlayerCards(g, clientId):
        pos = g.GetPlayerPosition(clientId)
        playerName = g.clients[clientId].name

        if (g.state == g.stWaitingForDiscard) and (g.GetVar(PlayerChoiceVar(pos)) == "pass"):
            print("Player", playerName, "opens cards but he's not the one having contract, ignored")
            return
        
        for i in range(g.GetPlayerCount()):
            g.OpenCardPile(PlayerCardsVar(pos), g.players[i])
            
        g.SendUpdate()

    def ClosePlayerCards(g, clientId):
        pos = g.GetPlayerPosition(clientId)
        playerName = g.clients[clientId].name

        if (g.state == g.stWaitingForDiscard) and (g.GetVar(PlayerChoiceVar(pos)) == "pass"):
            print("Player", playerName, "closes cards but he's not the one having contract, ignored")
            return
        
        g.CloseCardPile(PlayerCardsVar(pos))
        g.OpenCardPile(PlayerCardsVar(pos), g.players[pos])
        g.SendUpdate()

    def FinishRoundCommand(g, client, arg):
        g.HandleEvent(g.eWantsFinishRound, client.id)
    
    def PlayerWantsFinishRound(g, clientId):
        pos = g.GetPlayerPosition(clientId)
        g.wantsFinishRound[pos] = True;
        
        finishList = functools.reduce(lambda s1, s2: s1+" "+s2, \
                                      (str(i) for i in range(len(g.wantsFinishRound)) if g.wantsFinishRound[i]), \
                                      "").strip()
        g.SetVar("wantfinish", finishList)
        if all(g.wantsFinishRound):
            g.FinishRound()
        g.SendUpdate()

    def ShareCardsCommand(g, client, arg):
        g.HandleEvent(g.eShareCards, client.id)
    
    def PlayerSharesCards(g, clientId):
        pos = g.GetPlayerPosition(clientId)
        playerName = g.clients[clientId].name

        if g.GetVar(PlayerChoiceVar(pos)) != "":
            print("Player", playerName, "wants to share cards but he's the one having contract, ignored")
            return
        
        sharedWithPos = next(p for p in range(g.GetPlayerCount()) if (p != pos) and (g.GetVar(PlayerChoiceVar(p)) == ""))
        otherName = g.players[sharedWithPos].name
        if not g.IsCardPileOpen(PlayerCardsVar(pos), g.players[sharedWithPos]):
            print("Player", playerName, "wants to share cards with", otherName, "but he didn't open cards, ignored")
            return
        
        g.SetVar(PlayerShareVar(pos), sharedWithPos)
        g.SendUpdate()

    def MoveForCommand(g, client, arg):
        [pos, card] = arg
        g.HandleEvent(g.eMoveFor, [client.id, pos, card])
    
    def PlayerMovesForAnother(g, arg):
        [clientId, movePos, card] = arg
        pos = g.GetPlayerPosition(clientId)
        playerName = g.clients[clientId].name
        otherName = g.players[movePos].name

        if g.GetVar(PlayerShareVar(movePos)) != pos:
            print("Player ", playerName, " wants to move for ", otherName, " but was not shared with, ignored")
            return
        g.HandleEvent(g.eMove, [g.players[movePos].id, card])

    def EditScoreCommand(g, client, arg):
        [var, value] = arg
        g.HandleEvent(g.eEditScore, [var, value])

    def EditScore(g, arg):
        [var, value] = arg
        if value != g.GetVar(var):
            g.SetVar(var, value)
            g.SendUpdate()
