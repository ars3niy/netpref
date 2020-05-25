var suitValues = {"s": 1, "c": 2, "d": 3, "h": 4};

function compareSuites(s1, s2)
{
    return suitValues[s1] - suitValues[s2];
}

var valueValues = {"7": 7, "8": 8, "9": 9, "T": 10, "J": 11, "Q": 12, "K": 13, "A": 14};

function compareValues(v1, v2)
{
    return valueValues[v1] - valueValues[v2];
}

function compareCards(c1, c2)
{
    if (c1 == "*")
        if (c2 == "*")
            return 0;
        else
            return -1;
    else if (c2 == "*")
        return 1;
    else {
        var value1 = c1.charAt(0);
        var suit1 = c1.charAt(1);
        var value2 = c2.charAt(0);
        var suit2 = c2.charAt(1);
        
        if (suit1 != suit2)
            return compareSuites(suit1, suit2);
        else
            return compareValues(value1, value2);
    }
}

function Cards_ParseCards(s)
{
    result = [];
    if (s.charAt(0) == "*") {
        result = [];
        var n = parseInt(s.substring(1))
        for (var i = 0; i < n; i++)
            result.push("*");
    } else
        result = s.split(" ");

    result.sort(compareCards);
    return result;
}

var cardValues = ["7", "8", "9", "T", "J", "Q", "K", "A"];
var cardSuites = ["s", "c", "d", "h"];
const cardWidth = 92;
const cardHeight = 125;
var cardImages = null;

function loadImage(filename)
{
    var element = document.createElement("img");
    element.setAttribute("src", filename);
    element.setAttribute("width", cardWidth);
    element.setAttribute("height", cardHeight);
    return element;
}

function Cards_LoadCardImages(setName, doneCallback)
{
    var nextCardImages = [];
    var imagesRemaining = cardSuites.length*cardValues.length+1;
    var onImageLoaded = function(image) {
        imagesRemaining--;
        if (imagesRemaining == 0) {
            cardImages = nextCardImages;
            doneCallback();
        }
    };
    nextCardImages["*"] = loadImage("images/" + setName + "/back.png");
    nextCardImages["*"].onload = onImageLoaded;
    for (var v = 0; v < cardValues.length; v++)
        for (var s = 0; s < cardSuites.length; s++) {
            var card = cardValues[v] + cardSuites[s];
            nextCardImages[card] = loadImage("images/" + setName + "/" + card + ".png");
            nextCardImages[card].onload = onImageLoaded;
        }
}

var cardsRaised = [];
var maxRaisedCards = 0;
var positionsToRaise = [];

function Cards_ResetRaisedCards()
{
    cardsRaised = [];
    maxRaisedCards = 0;
    positionsToRaise = [];
}

function Cards_ResetRaisedCardsFor(position)
{
    for (var i = cardsRaised.length-1; i >= 0; i--)
        if (cardsRaised[i].position == position)
            cardsRaised.splice(i, 1);
}

function Cards_AllowRaiseCards(maxRaised, positions)
{
    maxRaisedCards = maxRaised;
    positionsToRaise = positions;
}

function Cards_GetRaisedCards(position)
{
    var result = [];
    for (var i = 0; i < cardsRaised.length; i++)
        if (cardsRaised[i].position == position)
            result.push(cardsRaised[i]);
    return result;
}

function Cards_ClickCard(clickedCard)
{
    if (positionsToRaise.indexOf(clickedCard.position) < 0)
        return false;
    
    for (var i = 0; i < cardsRaised.length; i++)
        if ((cardsRaised[i].x == clickedCard.x) && (cardsRaised[i].y == clickedCard.y)) {
            cardsRaised.splice(i, 1);
            return true;
        }
    
    var firstRaisedThisPos = -1;
    var numRaisedThisPos = 0;
    for (var i = 0; i < cardsRaised.length; i++) {
        if (cardsRaised[i].position == clickedCard.position) {
            if (firstRaisedThisPos < 0)
                firstRaisedThisPos = i;
            numRaisedThisPos++;
        }
    }
    
    if (numRaisedThisPos == maxRaisedCards) {
        cardsRaised.splice(firstRaisedThisPos, 1);
    }

    cardsRaised.push({card: clickedCard.card, position: clickedCard.position,
                    x: clickedCard.x, y: clickedCard.y});
    return true;
}

var cardsPainted = [];

function Cards_ClearPainted()
{
    cardsPainted = [];
}

function Cards_DrawCard(ctx, x, y, card, position, scale)
{
    var ynew = y;
    for (var i = 0; i < cardsRaised.length; i++)
        if ((cardsRaised[i].x == x) && (cardsRaised[i].y == y))
            ynew -= 10;
    ctx.drawImage(cardImages[card], x, ynew, cardWidth*scale, cardHeight*scale);
    cardsPainted.push({card: card, position: position, x: x, y: y});
}

function Cards_GetCardAt(x, y)
{
    for (var i = cardsPainted.length-1; i >= 0; i--)
        if ((x >= cardsPainted[i].x) && (x <= cardsPainted[i].x + cardWidth) &&
            (y >= cardsPainted[i].y) && (y <= cardsPainted[i].y + cardHeight)) 
            break;
    
    if (i < 0)
        return null;
    return cardsPainted[i];
}
