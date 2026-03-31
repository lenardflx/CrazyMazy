
from client.state.languages import languages as langs
from shared.protocol import ErrorCode, DisplayMessage

english = langs.ENGLISH.value
german  = langs.GERMAN.value

messages = {
    ErrorCode.GAME_NOT_FOUND: {
        english: "This game does not exist.",
        german: "Dieses Spiel existiert nicht."
    },
    ErrorCode.NO_PUBLIC_LOBBY: {
        english: "No public lobby available right now.",
        german: "Derzeit ist keine öffentliche Lobby verfügbar."
    },
    DisplayMessage.SERVER_NOT_REACHABLE: {
        english: "Server not reachable.",
        german: "Server kann nicht erreicht werden."
    },
    DisplayMessage.UNKNOWN_MESSAGE_TYPE: {
        english: "Error loading message, unknown message type.",
        german: "Fehler beim Laden der Nachricht. Unbekannter Nachrichtentyp."
    },
}
