"""Static translation catalog for supported client languages."""

from client.lang.messages import DisplayMessage, MessageKey
from client.state.languages import languages as langs
from shared.protocol import ErrorCode


MESSAGES: dict[langs, dict[MessageKey, str]] = {
    langs.ENGLISH: {
        ErrorCode.GAME_NOT_FOUND: "This game does not exist",
        ErrorCode.NO_PUBLIC_LOBBY: "No public lobby available right now",
        DisplayMessage.SERVER_NOT_REACHABLE: "Server not reachable",
        DisplayMessage.MAIN_MENU_CREATE: "Create",
        DisplayMessage.MAIN_MENU_JOIN: "Join",
        DisplayMessage.MAIN_MENU_TUTORIAL: "Tutorial",
        DisplayMessage.MAIN_MENU_OPTIONS: "Options",
        DisplayMessage.MAIN_MENU_QUIT: "Quit",
        DisplayMessage.MAIN_MENU_WELCOME: "Welcome",
        DisplayMessage.MAIN_MENU_START_WITH_TUTORIAL: "Start with the tutorial?",
        DisplayMessage.MAIN_MENU_START: "Start",
        DisplayMessage.MAIN_MENU_SKIP: "Skip",
        DisplayMessage.MAIN_MENU_QUIT_TITLE: "Quit Game?",
        DisplayMessage.MAIN_MENU_QUIT_MESSAGE: "Close the client now?",
        DisplayMessage.MAIN_MENU_CONNECTED_TO: "Connected to",
    },
    langs.GERMAN: {
        ErrorCode.GAME_NOT_FOUND: "Dieses Spiel existiert nicht",
        ErrorCode.NO_PUBLIC_LOBBY: "Derzeit ist keine öffentliche Lobby verfügbar",
        DisplayMessage.SERVER_NOT_REACHABLE: "Server nicht erreichbar",
        DisplayMessage.MAIN_MENU_CREATE: "Erstellen",
        DisplayMessage.MAIN_MENU_JOIN: "Beitreten",
        DisplayMessage.MAIN_MENU_TUTORIAL: "Tutorial",
        DisplayMessage.MAIN_MENU_OPTIONS: "Optionen",
        DisplayMessage.MAIN_MENU_QUIT: "Beenden",
        DisplayMessage.MAIN_MENU_WELCOME: "Willkommen",
        DisplayMessage.MAIN_MENU_START_WITH_TUTORIAL: "Mit dem Tutorial starten?",
        DisplayMessage.MAIN_MENU_START: "Starten",
        DisplayMessage.MAIN_MENU_SKIP: "Ueberspringen",
        DisplayMessage.MAIN_MENU_QUIT_TITLE: "Spiel beenden?",
        DisplayMessage.MAIN_MENU_QUIT_MESSAGE: "Client jetzt schliessen?",
        DisplayMessage.MAIN_MENU_CONNECTED_TO: "Verbunden mit",
    },
}
