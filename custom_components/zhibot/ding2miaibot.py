
#
from .dingbot import dingbotView

# Logging
import logging
_LOGGER = logging.getLogger(__name__)


#
class ding2miaibotView(dingbotView):

    async def handle(self, data):
        return data['text']['content']
