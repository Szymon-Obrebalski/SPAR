import requests
from imports.passwords import *


class SynologyClient:
    def __init__(self, ip: str = IP, port: int = PORT):
        self.base_url = f"http://{ip}:{port}/webapi"
        self.login = os.environ.get('login')
        self.password = os.environ.get('password')
        self.synotoken = None
        self.sid = None
        self.device_info = {
            "device_name": DEVICE_NAME,
            "device_id": DEVICE_ID
        }
        self.session = requests.Session()

    @property
    def base_params(self):
        return {
            "version": "5",
            "account": self.login,
            "passwd": self.password,
            "enable_syno_token": "yes",
            **self.device_info
        }

    @property
    def headers(self):
        return {
            'X-SYNO-TOKEN': self.synotoken
        } if self.synotoken else {}

    def synologin(self) -> bool:
        url = f'{self.base_url}/auth.cgi'
        params = self.base_params | {
            "api": "SYNO.API.Auth",
            "method": "login",
        }
        response = self.session.get(url, params=params)
        if response.status_code == 200 and response.json()['success']:
            self.synotoken = response.json()['data']['synotoken']
            self.sid = response.json()['data']['sid']
            return True

    def synocaltodolist(self):
        url = f'{self.base_url}/entry.cgi'
        params = {
            "api": "SYNO.Cal.Todo",
            "version": "5",
            "method": "list",
            "_sid": self.sid
        }
        response = self.session.get(url, params=params, headers=self.headers)
        if response.status_code == 200 and response.json()['success']:
            return response.json()
        return False

    def synocaltodoget(self, evt_id):
        url = f'{self.base_url}/entry.cgi'
        params = {
            "api": "SYNO.Cal.Todo",
            "version": "5",
            "method": "get",
            "_sid": self.sid,
            "evt_id": evt_id
        }
        response = self.session.get(url, params=params, headers=self.headers)
        if response.status_code == 200 and response.json()['success']:
            return response.json()
        return False

    def synocaltododelete(self, evt_id):
        url = f'{self.base_url}/entry.cgi'
        params = {
            "api": "SYNO.Cal.Todo",
            "version": "5",
            "method": "delete",
            "_sid": self.sid,
            "evt_id": evt_id
        }
        response = self.session.get(url, params=params, headers=self.headers)
        if response.status_code == 200 and response.json()['success']:
            return response.json()
        return False

    def synologout(self) -> bool:
        url = f'{self.base_url}/auth.cgi'
        params = {
            "api": "SYNO.API.Auth",
            "version": "1",
            "method": "logout",
            "_sid": self.sid
        }
        response = self.session.get(url, params=params, headers=self.headers)
        if response.status_code == 200 and response.json()['success']:
            return True


def main():
    ...


def getwishlist(calendar: str) -> list[str]:
    syno = SynologyClient()
    syno.synologin()
    wishlist = []
    if syno.synocaltodolist():
        for each in syno.synocaltodolist()['data']['list']:
            if each['original_cal_id'] == f'/bulikaxel/{calendar}/':
                wishlist.append(each['summary'])
                syno.synocaltododelete(each["evt_id"])
    syno.synologout()
    return wishlist


if '__main__' == __name__:
    main()
