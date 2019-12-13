
# Logging
import logging
_LOGGER = logging.getLogger(__name__)

DOMAIN = 'dingding'

# 
from homeassistant.components.http import HomeAssistantView
from homeassistant.helpers.state import AsyncTrackStates

# Config
import voluptuous as vol
import homeassistant.helpers.config_validation as cv

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required('senderId'): cv.string,
        }),
    }, extra=vol.ALLOW_EXTRA)

# 
_hass = None
_senderId = None

#
async def async_setup(hass, config):
    global _hass, _senderId
    _hass = hass
    conf = config[DOMAIN]
    _senderId = conf['senderId']
    hass.http.register_view(DingDingView)
    return True

#
class ChatView(HomeAssistantView):
    """View to handle Configuration requests."""
    name = DOMAIN
    url = '/' + DOMAIN
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

#
class DingDingView(ChatView):

    def response(self, answer):
        return {"msgtype": "text", "text": {"content": answer}}

    def check(self, data):
        #_LOGGER.debug("TOKEN: <%s>~=<%s>", data['senderId'], _senderId)
        return data['senderId'] == _senderId

    async def handle(self, data):
        return await hassQuery(data['text']['content'])

async def hassQuery(question):
    query = question.strip()
    _LOGGER.debug("QUERY: %s", query)
    if not query:
        return "少说空话"

    states = _hass.states.async_all()
    names = [] if query == "全部设备" else None

    answer = await hassStates(query, states, False, names) # 先尝试处理设备
    if answer is not None:
       return answer

    if names is not None:
        import locale
        locale.setlocale(locale.LC_COLLATE, 'zh_CN.UTF8')
        names = sorted(names, cmp=locale.strcoll)

    answer = await hassStates(query, states, True, names) # 再尝试处理分组
    if answer is not None:
        return answer

    if names is not None:
        return ','.join(names)

    return "未找到设备"

async def hassStates(query, states, group, names):
    for state in states:
        entity_id = state.entity_id
        if entity_id.startswith('zone') or entity_id.startswith('automation') or group != entity_id.startswith('group'):
            continue

        attributes = state.attributes
        friendly_name = attributes.get('friendly_name')
        if friendly_name is None:
            continue

        if names is not None:
            names.append(friendly_name)
        elif query.startswith(friendly_name) or query.endswith(friendly_name):
            action = hassAction(entity_id, query)
            return friendly_name + await hassState(entity_id, state.state, action)
    return None

STATE_NAMES = {
    'on': '开启状态',
    'off': '关闭状态',

    'home': '在家',
    'not_home': '离家',

    'cool': '制冷模式',
    'heat': '制热模式',
    'auto': '自动模式',
    'dry': '除湿模式',
    'fan': '送风模式',

    'open': '打开状态',
    'opening': '正在打开',
    'closed': '闭合状态',
    'closing': '正在闭合',

    'unavailable': '不可用',
}

async def hassState(entity_id, state, action):
    cover = entity_id.startswith('cover') or entity_id == 'group.all_covers'
    domain = 'cover' if cover else 'homeassistant'
    #domain = entity_id[:entity_id.find('.')]
    if action == '打开':
        service = 'open_cover' if cover else 'turn_on'
    elif action == '关闭':
        service = 'close_cover' if cover else 'turn_off'
    else:
        return '为' + (STATE_NAMES[state] if state in STATE_NAMES else state)

    data = {'entity_id': entity_id}
    with AsyncTrackStates(_hass) as changed_states:
        result = await _hass.services.async_call(domain, service, data, True)

    return action + ("成功" if result else "不成功")

def hassAction(entity_id, query):
    if not entity_id.startswith('sensor') and not entity_id.startswith('binary_sensor') and not entity_id.startswith('device_tracker'):
        if query.startswith('打开') or query.startswith('开') or query.endswith('打开'):
            return '打开'
        elif query.startswith('关') or query.endswith('关掉') or query.endswith('关闭') or query.endswith('关上'):
            return '关闭'
    return '查询'
