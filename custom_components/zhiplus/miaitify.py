#!/usr/bin/env python3
# encoding: utf-8

import json
import requests
import os,re,random,string
import hashlib
import time
import base64
from urllib import parse

import logging
_LOGGER = logging.getLogger(__name__)
_request = requests.session()

def miai_request(deviceId, method, path, message):
    try:
        requestId = ''.join(random.sample(string.ascii_letters + string.digits, 30))
        url = "https://api.mina.mi.com/remote/ubus?deviceId=%s&message=%s&method=%s&path=%s&requestId=%s" % (deviceId, parse.quote(json.dumps(message, ensure_ascii=False)), method, path, requestId) 
        r = _request.post(url)
        result = json.loads(r.text)
        if result['message'] == 'Success':
            return True
        else:
            if result['error'] == 'Unauthorized':
                _LOGGER.error('Unauthorized')
                #TODO: self.login_resutl = False
            else:
                _LOGGER.error(result)
    except BaseException as e:
        _LOGGER.error(e)
    return False

def miai_text_to_speech(deviceId, text):
    return miai_request(deviceId, 'text_to_speech', 'mibrain', {'text':text})

def miai_player_set_volume(deviceId, cookie, volume):
    return miai_request(deviceId, 'player_set_volume', 'mediaplayer', {'volume':volume, 'media':'app_ios'})

def miai_login(user, password):
    sign, pass_trace = miai_serviceLogin()
    if sign is None or pass_trace is None:
        _LOGGER.warning("miai_serviceLogin Failed")
        return None

    auth_result = miai_serviceLoginAuth2(user, password, sign, pass_trace)
    if auth_result is None:
        _LOGGER.warning('miai_serviceLoginAuth2 Failed')
        return None

    code = auth_result['code']
    if code == 0:
        cookies = miai_login_miai(auth_result['location'], auth_result['nonce'], auth_result['ssecurity'])
        if cookies is None:
            _LOGGER.warning('miai_login_miai Failed')
            return None
       
        devices = miai_device_list(cookies['userId'], cookies['serviceToken'])
        if devices is None:
            _LOGGER.warning('miai_device_list Failed')
        return devices

    elif code == 87001:
        _LOGGER.error('Need capt code')
    elif code == 70016:
        _LOGGER.error('Incorrect password')
    else:
        _LOGGER.error(result)
    return None

def miai_serviceLogin():
    url = 'https://account.xiaomi.com/pass/serviceLogin?sid=micoapi'
    pattern = re.compile(r'_sign":"(.*?)",')
    try:
        r = _request.get(url)
        pass_trace = _request.cookies.get_dict()['pass_trace']
        sign = pattern.findall(r.text)[0]
        return (sign, pass_trace)
    except BaseException as e:
        _LOGGER.warning(e)
        return (None, None)

def miai_serviceLoginAuth2(user, password, sign, pass_trace, captCode=None, ick=None):
    url='https://account.xiaomi.com/pass/serviceLoginAuth2'
    data = {
        '_json':'true',
        '_sign': sign,
        'callback': 'https://api.mina.mi.com/sts',
        'hash': hashlib.md5(password.encode('utf-8')).hexdigest().upper(),
        'qs': '%3Fsid%3Dmicoapi',
        'serviceParam': '{"checkSafePhone":false}',
        'sid': 'micoapi',
        'user': user
        }

    try:
        if captCode:
            url += '?_dc=' + str(int(round(time.time() * 1000)))
            data['captCode'] = captCode
            _headers['Cookie'] += '; ick=' + ick
        response =  _request.post(url, data=data)
        return json.loads(response.text[11:])
    except BaseException as e:
        _LOGGER.error(e)
        return None

def miai_login_miai(url, nonce, ssecurity):
    token = 'nonce=' + str(nonce) + '&' + ssecurity
    sha1 = hashlib.sha1(token.encode('utf-8')).digest()
    clientSign = base64.b64encode(sha1)
    url += '&clientSign=' + parse.quote(clientSign.decode())
    try:
        r = _request.get(url)
        if r.status_code == 200:
            return _request.cookies.get_dict()
        else:
            return None
    except BaseException as e:
        _LOGGER.warning(e)
        return None

def miai_device_list(userId, serviceToken):
    #requestId = 'CdPhDBJMUwAhgxiUvOsKt0kwXThAvY'
    requestId = ''.join(random.sample(string.ascii_letters + string.digits, 30))
    url = 'https://api.mina.mi.com/admin/v2/device_list?master=1&requestId=' + requestId
    try:
        rsponse = _request.get(url)
        return json.loads(rsponse.text)['data']
    except BaseException as e:
        _LOGGER.error(e)
        return None

if __name__ == '__main__':
    import sys
    devices = miai_login(sys.argv[1], sys.argv[2])
    if devices:
        miai_text_to_speech(devices[0]['deviceID'], "测试")
