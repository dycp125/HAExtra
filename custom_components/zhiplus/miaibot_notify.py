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

def miai_request(deviceId, cookie, method, path, message):
    try:
        requestId = ''.join(random.sample(string.ascii_letters + string.digits, 30))
        url = "https://api.mina.mi.com/remote/ubus?deviceId=%s&message=%s&method=%s&path=%s&requestId=%s" % (deviceId, parse.quote(json.dumps(message, ensure_ascii=False)), method, path, requestId) 
        r = requests.session().post(url, headers={'Cookie': cookie})
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

def miai_text_to_speech(deviceId, cookie, text):
    return miai_request(deviceId, cookie, 'text_to_speech', 'mibrain', {'text':text})

def miai_player_set_volume(deviceId, cookie, volume):
    return miai_request(deviceId, cookie, 'player_set_volume', 'mediaplayer', {'volume':volume, 'media':'app_ios'})

_headers = {
    'Host': 'account.xiaomi.com',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9'
    }

def miai_login(user, password):
    sign, pass_trace = miai_serviceLogin()
    if sign is None or pass_trace is None:
        _LOGGER.warning("miai_serviceLogin Failed")
        return None

    result = miai_serviceLoginAuth2(user, password, sign, pass_trace)
    if result is None:
        _LOGGER.warning('miai_serviceLoginAuth2 Failed')
        return None

    code = result['code']
    if code == 0:
        result = miai_login_miai(result['location'], result['nonce'], result['ssecurity'])
        if result is None:
            _LOGGER.warning('miai_login_miai Failed')
            return None
       
        result = miai_device_list(result['userId'], result['serviceToken'])
        if result is None:
            _LOGGER.warning('miai_device_list Failed')
        return result

    elif code == 87001:
        self._headers['Cookie']=self._headers['Cookie']+'; pwdToken={}'.format(self._cookies['pwdToken'])
        path = os.path.dirname(hass_frontend.__file__)
        try:
            current_time= int(round(time.time() * 1000))
            r= _request.get('https://account.xiaomi.com/pass/getCode?icodeType=login&{}'.format(current_time),headers=self._headers,timeout=3,cookies=self._cookies,verify=False)
            self._cookies['ick']=_request.cookies.get_dict()['ick']
            if os.access(path+'/images',os.W_OK):
                with open(path+'/images'+'/miai{}.jpg'.format(current_time),'wb') as f:
                    f.write(r.content)
                    f.close()
                self.request_app_setup(current_time)
        except IOError as e:
            _LOGGER.warning(e)
        except BaseException as e:
            _LOGGER.warning(e)
    elif code == 70016:
        _LOGGER.error('Incorrect password')
    else:
        _LOGGER.error(result)
    return None

def miai_serviceLogin():
    url = 'https://account.xiaomi.com/pass/serviceLogin?sid=micoapi'
    pattern = re.compile(r'_sign":"(.*?)",')
    try:
        r = _request.get(url, headers=_headers)
        pass_trace = _request.cookies.get_dict()['pass_trace']
        sign = pattern.findall(r.text)[0]
        return (sign, pass_trace)
    except BaseException as e:
        _LOGGER.warning(e)
        return (None, None)

def miai_serviceLoginAuth2(user, password, sign, pass_trace, captCode=None, ick=None):
    url='https://account.xiaomi.com/pass/serviceLoginAuth2'
    _headers['Content-Type'] = 'application/x-www-form-urlencoded'
    _headers['Accept'] = '*/*'
    _headers['Origin'] = 'https://account.xiaomi.com'
    _headers['Referer'] = 'https://account.xiaomi.com/pass/serviceLogin?sid=micoapi'
    _headers['Cookie'] = 'pass_trace={}'.format(pass_trace)

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

        response =  _request.post(url, headers=_headers, data=data)
        #_cookies['pwdToken'] = _request.cookies.get_dict()['passToken']
        return json.loads(response.text[11:])
    except BaseException as e:
        _LOGGER.error(e)
        return None

def miai_login_miai(url, nonce, ssecurity):
    token = 'nonce=' + str(nonce) + '&' + ssecurity
    sha1 = hashlib.sha1(token.encode('utf-8')).digest()
    clientSign = base64.b64encode(sha1)
    url += '&clientSign=' + parse.quote(clientSign.decode())
    headers = {'User-Agent': 'MISoundBox/1.4.0,iosPassportSDK/iOS-3.2.7 iOS/11.2.5','Accept-Language': 'zh-cn','Connection': 'keep-alive'}
    try:
        r = _request.get(url, headers=headers)
        if r.status_code == 200:
            return _request.cookies.get_dict()
        else:
            return None
    except BaseException as e :
        _LOGGER.warning(e)
        return None

def miai_device_list(userId, serviceToken):
    #requestId = 'CdPhDBJMUwAhgxiUvOsKt0kwXThAvY'
    requestId = ''.join(random.sample(string.ascii_letters + string.digits, 30))
    url = 'https://api.mina.mi.com/admin/v2/device_list?master=1&requestId=' + requestId
    headers = {'Cookie': 'userId=' + userId + ';serviceToken=' + serviceToken}
    try:
        rsponse = _request.get(url, headers = headers)
        #return json.loads(rsponse.text)['data']

        deviceId = json.loads(rsponse.text)['data']
        headers['deviceId'] = deviceId
        return headers
    except BaseException as e :
        _LOGGER.error(e)
        return None

result = miai_login('xxx', 'xxx')
if result:
    miai_text_to_speech(result['deviceId'][0]['deviceID'], result, "测试")
