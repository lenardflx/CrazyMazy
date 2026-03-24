# Author: Lenard Felix

from client.network.state import ClientState
from shared.dispatch import Dispatcher

dispatcher: Dispatcher[ClientState, None] = Dispatcher()
