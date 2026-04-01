"""Language service used by client screens to resolve localized UI text."""

from client.lang.catalog import MESSAGES
from client.lang.messages import DisplayMessage, MessageKey
from client.state.app_data import ClientData
from client.state.languages import languages as langs
from shared.protocol import ErrorCode


class LanguageService:
    """Resolve a message key to the active client language with English fallback."""

    def _current_language(self) -> langs:
        """Return the currently configured client language."""
        return ClientData().get_language()

    def get_message(self, message: MessageKey) -> str:
        """Return localized text for a message key, falling back to English."""
        # localized message
        localized_messages = MESSAGES.get(self._current_language(), {})
        if message in localized_messages:
            return localized_messages[message]

        # fallback to english
        fallback_messages = MESSAGES[langs.ENGLISH]
        if message in fallback_messages:
            return fallback_messages[message]

        # missing key
        if isinstance(message, DisplayMessage):
            return f"msg::{message}"
        if isinstance(message, ErrorCode):
            return f"err::{message}"
        return f"msg::{message}"
