import requests

from detect_sdk.models.account import verify_credentials


class AccountController:

    def __init__(self, account):
        self.account = account

    @verify_credentials
    def register(self, email):
        res = requests.post(url=f'{self.account.hq}/account', json=dict(email=email), headers=self.account.headers)
        if res.status_code == 200:
            return res.json()
        raise Exception(f'Failed to register account (reason:{res.status_code})')

    @verify_credentials
    def create_user(self, permission, email):
        res = requests.post(
            url=f'{self.account.hq}/account/user',
            json=dict(permission=permission, email=email),
            headers=self.account.headers
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(f'Failed to create user (reason:{res.status_code})')

    @verify_credentials
    def delete_user(self, email):
        res = requests.delete(f'{self.account.hq}/account/user', json=dict(email=email), headers=self.account.headers)
        if res.status_code == 200:
            return True
        raise Exception(f'Failed to delete user (reason:{res.status_code})')

    @verify_credentials
    def describe_account(self):
        res = requests.get(f'{self.account.hq}/account', headers=self.account.headers)
        if res.status_code == 200:
            return res.json()
        raise Exception(f'Failed to find account (reason:{res.status_code})')

    @verify_credentials
    def update_token(self, token):
        """ Update Account token """
        res = requests.put(f'{self.account.hq}/account', headers=self.account.headers, json=dict(token=token))
        if res.status_code != 200:
            raise Exception(f'Failed to update token (reason:{res.status_code})')
        cfg = self.account.read_keychain_config()
        cfg[self.account.profile]['token'] = token
        self.account.write_keychain_config(cfg)

    @verify_credentials
    def describe_activity(self, days=7):
        """ Get a summary of Account activity """
        params = dict(days=days)
        res = requests.get(f'{self.account.hq}/account/activity', headers=self.account.headers, params=params)
        if res.status_code == 200:
            return res.json()
        raise Exception(f'Failed to get activity (reason:{res.status_code})')
