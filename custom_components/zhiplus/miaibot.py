
# Logging
import logging
_LOGGER = logging.getLogger(__name__)

#
_hass = None
_conf = None

#
from .zhibot import zhibotQuery
from .chatbot import chatbotView
from homeassistant.components.http import KEY_REAL_IP

#
class miaibotView(chatbotView):

    async def post(self, request):
        self._open_mic = False
        self._real_ip = str(request[KEY_REAL_IP])
        return await super().post(request)

    def check(self, data):
        app_id = _conf.get('app_id')
        if app_id is not None and data['session']['application']['app_id'] != app_id:
            return False
        user_id = _conf.get('user_id')
        if user_id is not None and data['session']['user']['user_id'] != user_id:
            return False
        # else
        #     return True
        return self._real_ip.startswith('124.251')

    async def handle(self, data):

        request = data['request']

        #
        if 'no_response' in request:
            self._open_mic = True
            return "主人，您还在吗？"

        #
        request_type = request['type']
        if request_type == 2:
            return "再见主人，我在这里等你哦！"

        #
        slot_info = data['request'].get('slot_info')
        intent_name = slot_info.get('intent_name') if slot_info is not None else None
        if intent_name == 'Mi_Welcome':
            self._open_mic = True
            return "您好主人，我能为你做什么呢？"

        answer = await zhibotQuery(_hass, data['query'])
        self._open_mic = answer == "未找到设备"
        return answer

    def response(self, answer):
        return {
            'version': '1.0',
            'is_session_end': not self._open_mic,
            'response': {
                'open_mic': self._open_mic,
                'to_speak': {'type': 0, 'text': answer},
                #'to_display': {'type': 0,'text': text}
            }
        }
