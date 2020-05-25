from gamemodules import pref
import cardgame

class Game(pref.Game):
    def __init__(this, name):
        pref.Game.__init__(this, name)
        this.shuffleMethod = cardgame.SHUFFLE_FIXEDORDER

    def GetTypeName(this):
        return "rostovtest"

    def ChooseDealer(g):
        return 0
