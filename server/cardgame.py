import games
import functools
import random

class CardPileInfo:
    def __init__(this):
        this.visibleTo = []
    
    def Close(this):
        this.visibleTo = []
    
    def OpenTo(this, playerId):
        this.visibleTo += [playerId]

    def CloseFrom(this, playerId):
        this.visibleTo.remove(playerId)
    
    def IsOpenTo(this, playerId):
        return playerId in this.visibleTo

CARD_6 = "6"
CARD_7 = "7"
CARD_8 = "8"
CARD_9 = "9"
CARD_10 = "T"
CARD_J = "J"
CARD_Q = "Q"
CARD_K = "K"
CARD_A = "A"

SUIT_SPADE = "s"
SUIT_CLUB = "c"
SUIT_DIAMOND = "d"
SUIT_HEART = "h"

SHUFFLE_RANDOMORDER = "randomize"
SHUFFLE_FIXEDORDER = "fixed"

def EncodeCardPile(value):
    return functools.reduce(lambda s1, s2: s1 + " " + s2, value) if len(value)>0 else ""

def MakeCard(value, suit):
    return value+suit

class Deck:
    def __init__(this, cardlist):
        this.cardList = [c for c in cardlist]
        this.cards = [c for c in cardlist]
    
    def Restore(this):
        for card in this.cardList:
            if not card in this.cards:
                this.cards += [card]
    
    def Shuffle(this, method):
        if method == SHUFFLE_RANDOMORDER:
            cardsLeft = [c for c in this.cardList]
            this.cards = []
            for i in range(len(this.cardList)):
                ind = random.randint(0, len(cardsLeft)-1)
                this.cards += [cardsLeft.pop(ind)]
        elif method == SHUFFLE_FIXEDORDER:
            this.cards = [c for c in this.cardList]
        else:
            raise Exception("unknown shuffle method")
    
    def RemoveCards(this, amount):
        result = this.cards[len(this.cards)-amount:]
        this.cards = this.cards[0:len(this.cards)-amount]
        return result

class CardGame(games.Game):
    def __init__(this, name):
        games.Game.__init__(this, name)
        this.SetVar("position", 0)
        this.SetVarExtra("position", "playerposition")
    
    def CreateCardPile(this, name):
        this.SetVar(name, [])
        this.SetVarExtra(name, CardPileInfo())
    
    def DiscardCardPile(this, name):
        this.SetVar(name, [])
    
    def GetPlayerPosition(this, clientId):
        for i in range(len(this.players)):
            if this.players[i].id == clientId:
                return i
        raise Exception("Client id " + str(clientId) + " not found in game " + this.name)
    
    def OpenCardPile(this, name, toPlayer):
        this.GetVarExtra(name).OpenTo(this.GetPlayerPosition(toPlayer.id))
    
    def IsCardPileOpen(this, name, toPlayer):
        return this.GetVarExtra(name).IsOpenTo(this.GetPlayerPosition(toPlayer.id))
    
    def CloseCardPile(this, name, fromPlayer=None):
        if fromPlayer == None:
            this.GetVarExtra(name).Close()
        else:
            this.GetVarExtra(name).CloseFrom(this.GetPlayerPosition(toPlayer.id))
    
    def GetVarValueForPlayer(this, value, extra, clientId):
        if extra == "playerposition":
            return this.GetPlayerPosition(clientId)
        elif extra:
            if not this.GetPlayerPosition(clientId) in extra.visibleTo:
                return "*"+str(len(value)) if len(value)>0 else ""
            else:
                return EncodeCardPile(value)
        else:
            return value

    def DealToCardPile(this, deck, name, cardCount):
        try:
            value = this.GetVar(name)
        except:
            this.CreateCardPile(name)
            value = []
        this.SetVar(name, value + deck.RemoveCards(cardCount))

    def AddCardToPile(this, name, card):
        try:
            value = this.GetVar(name)
        except:
            this.CreateCardPile(name)
            value = []
        this.SetVar(name, value + [card])
