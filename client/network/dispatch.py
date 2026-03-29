# Author: Lenard Felix

"""
Event dispatcher for handling client-side events.
The context is the ClientState, which is passed to each handler method and can be used
to access the current state of the client connection.
The client does not respond to incoming events, so the return type of the handler methods is None. 
"""

from client.network.state import ClientState
from shared.events import EventDispatcher

dispatcher: EventDispatcher[ClientState, None] = EventDispatcher()
