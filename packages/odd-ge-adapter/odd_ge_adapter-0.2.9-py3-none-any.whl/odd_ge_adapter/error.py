from odd_ge_adapter.utils.secret import hide_secret


class AccountIdError(Exception):
    def __init__(self, key, secret):
        super().__init__(self._message(key, secret))

    @staticmethod
    def _message(key: str, secret: str):
        return f"Could not get account id for {hide_secret(key)}, {hide_secret(secret)}.\nSet env variable aws_account_id explicitly or check your Account"
