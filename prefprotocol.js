var websocket = null;
var name = null;
var debugTextArea = null;
var playerList = null;
var gameList = null;
var gameTypeList = null;
var playerName = null;
var onGameState = null;
var onJoinFail = null;
var onConnectExternal = null;
var onDisconnectExternal = null;

const ST_NOT_CONNECTED = 0;
const ST_JUST_CONNECTED = 1;
const ST_SENT_NAME = 2;
const ST_LOBBY = 3;
const ST_JUST_JOINED = 4;
const ST_GAME = 5;

var state = ST_NOT_CONNECTED;

function Game_IsConnected()
{
    return state != ST_NOT_CONNECTED;
}

function Game_CanJoin()
{
    return state == ST_LOBBY;
}

function debug(message)
{
    if (debugTextArea) {
        debugTextArea.value += message + "\n";
        debugTextArea.scrollTop = debugTextArea.scrollHeight;
    }
}

function Game_Disconnect() {
    if (websocket)
        websocket.close();
}

function onConnect(event)
{
    debug("connected")
    state = ST_JUST_CONNECTED;
}

function onDisconnect(event)
{
    debug("disconnected")
    clearGameTypes();
    clearLobby();
    state = ST_NOT_CONNECTED;
    onDisconnectExternal();
}

function encodeValue(s)
{
    var result = "";
    for (var i = 0; i < s.length; i++) {
        var c = s.charAt(i);
        if (c == '\"')
            result += "\\\"";
        else if (c == '\\')
            result += "\\\\";
        else
            result += c;
    }
    return "\"" + result + "\"";
}

function decodeValues(s)
{
    var result = [];
    
    i = 0;
    while (true) {
        while ((i < s.length) && (s.charAt(i) == ' ')) i++;
        if (i == s.length) break;
        namestart = i;
        while ((i < s.length) && (s.charAt(i) != '=')) i++;
        
        name = s.substring(namestart, i);
        value = "";
        i++;
        var quoted = false;
        if ((i < s.length) && (s.charAt(i) == '\"')) {
            quoted = true;
            i++;
        }
        
        while (i < s.length) {
            var c = s.charAt(i);
            if (!quoted && (c == ' ')) {
                break;
            } else if (quoted && (c == '\"')) {
                i++;
                break;
            } else if (!quoted) {
                value += c;
                i++;
            } else {
                if ((c == '\\') && (i+1 < s.length) && (s.charAt(i+1) == '\"')) {
                    value += '\"';
                    i += 2;
                } else if ((c == '\\') && (i+1 < s.length) && (s.charAt(i+1) == '\\')) {
                    value += '\\';
                    i += 2;
                } else {
                    value += c;
                    i++;
                }
            }
        }
        var element = [name, value];
        result.push(element);
    }
    
    return result;
}

function send(s)
{
    debug("Sent: " + s);
    websocket.send(s);
}

function sendName()
{
    send("name " + encodeValue(playerName));
}

function clearLobby()
{
    playerList.value = "";
    while (gameList.options.length > 0)
        gameList.remove(0);
}

function showLobby(values)
{
    clearLobby();
    for (var i = 0; i < values.length; i++) {
        var element = values[i];
        if (element[0] == "player") {
            playerList.value += element[1] + "\n";
        } else if (element[0] == "game") {
            var gamename = values[i][1];
            if ((i+1 < values.length) && (values[i+1][0] == "type")) {
                var gametype = values[i+1][1];
                var option = document.createElement("option");
                option.text = gamename + ": " + gametype;
                option.value = gamename;
                gameList.add(option);
                i++;
            }
        }
    }
}

function clearGameTypes()
{
    while (gameTypeList.options.length > 0)
        gameTypeList.remove(0);
}

function showGameTypes(values)
{
    clearGameTypes();
    for (var i = 0; i < values.length; i++)
        if (values[i][0] == "gametype") {
            var option = document.createElement("option");
            option.text = values[i][1];
            option.value = values[i][1];
            gameTypeList.add(option);
        }
}

function ReportGameState(s)
{
    var values = decodeValues(s);
    var state = "";
    for (var i = 0; i < values.length; i++)
        if (values[i][0] == "State")
            state = values[i][1];
    onGameState(state, values);
}

function onMessage(event)
{
    s = event.data;
    debug("[state=" + state + "] Received: " + s);
    if (state == ST_JUST_CONNECTED) {
        var values = decodeValues(s);
        if ((values.length >= 1) && (values[0][0] == "ack")) {
            state = ST_SENT_NAME;
            showGameTypes(values);
            sendName();
        }
    } else if (state == ST_SENT_NAME) {
        if (s == "nak") {
            Game_Disconnect();
            alert("This name is already used");
        } else {
            onConnectExternal();
            state = ST_LOBBY;
            var values = decodeValues(s);
            showLobby(values);
        }
    } else if (state == ST_LOBBY) {
        var values = decodeValues(s);
        showLobby(values);
    } else if (state == ST_JUST_JOINED) {
        if (s == "nak") {
            state = ST_LOBBY;
            onJoinFail();
        } else {
            state = ST_GAME;
            ReportGameState(s);
        }
    } else if (state == ST_GAME)
        ReportGameState(s);
}

function handleError(message)
{
    alert(message);
}

function onError(event)
{
    handleError("Error: " + event.data);
}

function Game_Init(debugAreaName, playerListName, gameListName, gameTypeListName,
                   connectFcn, disconnectFcn)
{
    if (debugAreaName) {
        debugTextArea = document.getElementById(debugAreaName);
    }
    playerList = document.getElementById(playerListName);
    gameList = document.getElementById(gameListName);
    gameTypeList = document.getElementById(gameTypeListName);
    onConnectExternal = connectFcn;
    onDisconnectExternal = disconnectFcn;
}

function Game_Connect(wsUri, name)
{
    playerName = name;
    try {
        if (typeof MozWebSocket == 'function')
            WebSocket = MozWebSocket;
        if ( websocket && websocket.readyState == 1 )
            websocket.close();
        websocket = new WebSocket( wsUri );
        websocket.onopen = onConnect;
        websocket.onclose = onDisconnect;
        websocket.onmessage = onMessage;
        websocket.onerror = onError;
    } catch (exception) {
        handleError("Exception: " + exception)
    }
}

function Game_JoinGame(gameName, gameStateFcn, joinFailFcn)
{
    onGameState = gameStateFcn;
    onJoinFail = joinFailFcn;
    state = ST_JUST_JOINED;
    send("join " + encodeValue(gameName));
}

function Game_CreateGame(gameName, gameType, gameStateFcn, createFailFcn)
{
    onGameState = gameStateFcn;
    onJoinFail = createFailFcn;
    state = ST_JUST_JOINED;
    send("creategame " + encodeValue(gameName) + " " + encodeValue(gameType));
}

function Game_Pass()
{
    send("pass");
}

function Game_OrderContract()
{
    send("order game");
}

function Game_Debug(message)
{
    debug(message);
}

function Game_ConfirmOrder(order, discard1, discard2)
{
    send("confirm " + order + " " + discard1 + " " + discard2);
}

function Game_Ready()
{
    send("ready");
}

function Game_MakeMove(card)
{
    send("move " + card);
}

function Game_ProposeFinish()
{
    send("finish");
}

function Game_OpenCards()
{
    send("open");
}

function Game_CloseCards()
{
    send("close");
}

function Game_ShareCards()
{
    send("share");
}

function Game_MakeMoveFor(otherPlayer, card)
{
    send("movefor " + otherPlayer + " " + card);
}

function Game_EditScore(parameter, newValue)
{
    send("editscore " + parameter + " " + newValue);
}
