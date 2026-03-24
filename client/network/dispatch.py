# Author: Lenard Felix

from client.network.state import ClientState
from shared.events import EventDispatcher

dispatcher: EventDispatcher[ClientState, None] = EventDispatcher()
