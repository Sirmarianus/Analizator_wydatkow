from flask_login import UserMixin


class User(UserMixin):
    active_wallet = 0
    def __init__(self, id):
        self.id = id

    def set_active_wallet(self, active_wallet):
        self.active_wallet = active_wallet

    def get_active_wallet(self):
        return self.active_wallet


def sql_injection_replace(word):
    disallowed_chars = "\'\"-!\b\n\r\t\\\%\0"
    for char in disallowed_chars:
        word = word.replace(char, '')
    return word