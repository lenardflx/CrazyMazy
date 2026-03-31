
from client.state.languages import languages as langs
from shared.protocol import ErrorCode, DisplayMessage

messages = {
    ErrorCode.GAME_NOT_FOUND: {
        langs.ENGLISH: "This game does not exist.",
        langs.GERMAN: "Dieses Spiel existiert nicht."
    },
    ErrorCode.NO_PUBLIC_LOBBY: {
        langs.ENGLISH: "No public lobby available right now.",
        langs.GERMAN: "Keine öffentliche Lobby ist zurzeit verfügbar."
    },
    DisplayMessage.SERVER_NOT_REACHABLE: {
        langs.ENGLISH: "Server not reachable.",
        langs.GERMAN: "Server kann icht erreicht werden."
    },
    DisplayMessage.UNKNOWN_MESSAGE_TYPE: {
        langs.ENGLISH: "Error loading message, unknown message type.",
        langs.GERMAN: "Fehler beim laden der Nachricht. Unbekannter Nachrichtentyp."
    },
}
