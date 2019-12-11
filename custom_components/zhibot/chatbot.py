
# Logging
import logging
_LOGGER = logging.getLogger(__name__)

#
class ChatBotView(HomeAssistantView):
    """View to handle Configuration requests."""
    url = '/' + name
    requires_auth = False

    async def post(self, request):
        try:
            data = await request.json()
            _LOGGER.debug("REQUEST: %s", data)
            answer = await self.handle(data) if self.check(data) else "没有访问权限！"
        except:
            import traceback
            _LOGGER.error(traceback.format_exc())
            answer = "程序出错啦！"
        _LOGGER.debug("RESPONSE: %s", answer)
        return self.json(self.response(answer))

    def response(self, answer):
        return None

    def check(self, data):
        return False

    async def handle(self, data):
        return "未能处理"
