# Author: Lenard Felix

from server.network.models import OutgoingMessage, RequestContext
from shared.dispatch import Dispatcher

dispatcher: Dispatcher[RequestContext, list[OutgoingMessage]] = Dispatcher()
