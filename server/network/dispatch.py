# Author: Lenard Felix

from server.network.models import OutgoingMessage, RequestContext
from shared.events import EventDispatcher

dispatcher: EventDispatcher[RequestContext, list[OutgoingMessage]] = EventDispatcher()
