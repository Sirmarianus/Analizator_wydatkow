from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, id):
        self.id = id


def sql_injection_replace(word):
    disallowed_chars = "\'\"-!\b\n\r\t\\\%\0"
    for char in disallowed_chars:
        word = word.replace(char, '')
    return word