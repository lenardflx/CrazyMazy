# Author: Lenard Felix

import socket

from shared.dispatch import Dispatcher

dispatcher: Dispatcher[socket.socket] = Dispatcher()