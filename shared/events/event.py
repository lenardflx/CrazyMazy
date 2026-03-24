from abc import ABC, abstractmethod

from shared.protocol import Message


class Event(ABC):
    @abstractmethod
    def to_message(self) -> Message:
        pass

class ClientJoinEvent(Event):
    def to_message(self) -> Message:
        pass

    @staticmethod
    def from_message(message: Message) -> 'ClientJoinEvent':
        pass