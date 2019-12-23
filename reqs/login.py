import base64
import requests
from io import BytesIO

try:
    from PIL import Image
except ImportError:
    Image = None
    
import utils


class LoginReq:
    @staticmethod
    async def logout(user):
        url = 'https://passport.bilibili.com/login?act=exit'
        json_rsp = await user.login_session.request_json('GET', url, headers=user.dict_bili['pcheaders'], is_login=True)
        return json_rsp

    @staticmethod
    async def fetch_key(user):
        url = 'https://passport.bilibili.com/api/oauth2/getKey'
        params = user.sort_and_sign()
        json_rsp = await user.login_session.request_json('POST', url, params=params, is_login=True)
        return json_rsp
        
    @staticmethod
    async def fetch_key_tv(user):
        url = 'https://passport.snm0516.aisee.tv/api/oauth2/getKey'
        temp_params = f'appkey={user.dict_bilitv["appkey"]}'
        sign = user.calc_sign_tv(temp_params)
        params = {'appkey': user.dict_bilitv['appkey'], 'sign': sign}
        json_rsp = await user.login_session.request_json('POST', url, data=params, is_login=True)
        return json_rsp

    @staticmethod
    async def fetch_capcha(user):
        url = "https://passport.bilibili.com/captcha"
        binary_rsp = await user.login_session.request_binary('GET', url)
        return binary_rsp

    @staticmethod
    async def login_tv(user, url_name, url_password, captcha=''):
        temp_params = f"appkey={user.dict_bilitv['appkey']}&build={user.dict_bilitv['build']}&captcha={captcha}&channel=master&guid=XYEBAA3E54D502E37BD606F0589A356902FCF&mobi_app=android_tv_yst&password={url_password}&platform=android&token=5598158bcd8511e2&ts=0&username={url_name}"
        sign = user.calc_sign_tv(temp_params)
        payload = f'{temp_params}&sign={sign}'
        url = "https://passport.snm0516.aisee.tv/api/tv/login"
        json_rsp = await user.login_session.request_json('POST', url, params=payload, is_login=True)
        return json_rsp
        
    @staticmethod
    async def login(user, url_name, url_password, captcha=''):
        extra_params = [
            f'captcha={captcha}',
            f'password={url_password}',
            f'username={url_name}'

        ]
        params = user.sort_and_sign(extra_params)
        url = "https://passport.bilibili.com/api/v3/oauth2/login"
        json_rsp = await user.login_session.request_json('POST', url, headers=user.dict_bili['appheaders'], params=params, is_login=True)
        return json_rsp
    @staticmethod
    async def access_token_2_cookies(user,access_token):
        temp_params = f"access_key={access_token}&appkey={user.dict_bilitv['appkey']}&gourl=https%3A%2F%2Faccount.bilibili.com%2Faccount%2Fhome"
        sign = user.calc_sign_tv(temp_params)
        payload = f'{temp_params}&sign={sign}'
        url = f"https://passport.bilibili.com/api/login/sso?{payload}"
        response = requests.get(url, allow_redirects=False)
        return response.cookies.get_dict(domain=".bilibili.com")
    @staticmethod
    async def is_token_usable(user):
        list_cookie = user.dict_bili['cookie'].split(';')
        extra_params = [
            f'access_key={user.dict_bili["access_key"]}',
            f'ts={utils.curr_time()}'
        ] + list_cookie
        params = user.sort_and_sign(extra_params)
        true_url = f'https://passport.bilibili.com/api/v3/oauth2/info'
        json_rsp = await user.login_session.request_json('GET', true_url, params=params, headers=user.dict_bili['appheaders'], is_login=True)
        return json_rsp

    @staticmethod
    async def refresh_token(user):
        list_cookie = user.dict_bili['cookie'].split(';')
        extra_params = [
            f'access_key={user.dict_bili["access_key"]}',
            f'access_token={user.dict_bili["access_key"]}',
            f'refresh_token={user.dict_bili["refresh_token"]}',
            f'ts={utils.curr_time()}'
        ] + list_cookie

        params = user.sort_and_sign(extra_params)
        url = f'https://passport.bilibili.com/api/v2/oauth2/refresh_token'
        json_rsp = await user.login_session.request_json('POST', url, headers=user.dict_bili['appheaders'], params=params, is_login=True)
        return json_rsp
        
    @staticmethod
    async def cnn_captcha(user, content):
        url = "http://152.32.186.69:19951/captcha/v1"
        str_img = base64.b64encode(content).decode(encoding='utf-8')
        json_rsp = await user.other_session.orig_req_json('POST', url, json={"image": str_img})
        captcha = json_rsp['message']
        print(f"此次登录出现验证码,识别结果为{captcha}")
        return captcha