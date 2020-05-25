var translationStrings = [
    "Toggle debug",
    "Server:",
    "Name:",
    "Connect",
    "Players:",
    "Games:",
    "Join game",
    "Game name:",
    "Game type:",
    "Create game",
    "Waiting for players to join...",
    "Waiting for players...",
    
    "Enter server",
    "Enter your name",
    "Already connected",
    "Not connected",
    "Failed to join game (maybe it's full)",
    "Failed to create game",
    "Cannot join game while not fully connected or in game",
    "No game selected",
    "Cannot create game while not fully connected or in game",
    "Enter game name",
    "No game type selected",
    
    "Bidding",
    "First to speak",
    "Pass",
    "Contract",
    "Discard 2 cards",
    "Spade",
    "Club",
    "Diamond",
    "Heart",
    "NT/Misere",
    "Start round",
    "Ready",
    "Not ready",
    "Put card",
    "To move",
    "Finish round",
    "Agreed to finish",
    "Open cards",
    "Close cards",
    "Let partner move for me",
    "Score",
    "Close",
    "Points to add"
];

var defaultTranslation = {
    "id": "default",
    "name": "English"
};

var rusTranslation = {
    "id":   "ru",
    "name": "Русский",
    
    "Toggle debug":                   "Отладка",
    "Card style:":                    "Картинки:",
    "Server:":                        "Сервер:",
    "Name:":                          "Имя:",
    "Connect":                        "Подключиться",
    "Players:":                       "Игроки:",
    "Games:":                         "Игры:",
    "Join game":                      "Присоединиться",
    "Game name:":                     "Название игры:",
    "Game type:":                     "Тип игры:",
    "Create game":                    "Создать игру",
    "Waiting for players to join...": "Ждём пока подключатся игроки...",
    "Waiting for players...":         "Ждём отключившихся игроков...",
    
    "Enter server":                          "Введи сервер",
    "Enter your name":                       "Введи имя",
    "Already connected":                     "Уже подключены",
    "Not connected":                         "Не подключены",
    "Failed to join game (maybe it's full)": "Не удалось войти в игру",
    "Failed to create game":                 "Не удалось создать игру",
    "Cannot join game while not fully connected or in game":
        "Нельзя войти в игру будучи не до конца подключены или в игре",
    "No game selected":                      "Выбери игру",
    "Cannot create game while not fully connected or in game":
        "Нельзя создать игру будучи не до конца подключены или в игре",
    "Enter game name":                       "Введи название игры",
    "No game type selected":                 "Тип игры не выбран",
    
    "Bidding":          "Торговля",
    "First to speak":   "Начинает говорить",
    "Pass":             "Пас",
    "Contract":         "Контракт",
    "Discard 2 cards":  "Снеси 2 карты",
    "Spade":            "Пика",
    "Club":             "Трефа",
    "Diamond":          "Бубна",
    "Heart":            "Черва",
    "NT/Misere":        "БК/Мизер",
    "Start round":      "Начать играть",
    "Ready":            "Готов",
    "Not ready":        "Не готов",
    "Put card":         "Положить карту",
    "To move":          "Ходит",
    "Finish round":     "Окончить раздачу",
    "Agreed to finish": "Соглашается окончить",
    "Open cards":       "Открыть карты",
    "Close cards":      "Закрыть карты",
    "Let partner move for me": "Дать ходить за меня",
    "Score":            "Пулька",
    "Close":            "Закрыть",
    "Points to add":    "Сколько очков добавить"
};

var translations = [defaultTranslation, rusTranslation];
var translation = defaultTranslation;

function _(s)
{
    var t = translation[s];
    if (!t)
        return s;
    else
        return t;
}

function Translate_SetLanguage(id)
{
    translation = defaultTranslation;
    for (var i = 0; i < translations.length; i++)
        if (translations[i]["id"] == id) {
            translation = translations[i];
            break;
        }
}

function Translate_GetLanguages()
{
    var result = [];
    for (var i = 0; i < translations.length; i++) {
        var id = translations[i]["id"];
        var name = translations[i]["name"];
        if (id && name) {
            result.push({id: id, name: name});
        }
    }
    return result;
}
