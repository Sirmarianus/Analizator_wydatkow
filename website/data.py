class data(object):
    _instance = None
    
    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            cls._id = 0
            cls._email = ''
            cls._is_logged = False
            cls._active_wallet = 0
        return cls._instance

    def is_logged(self):
        return self._is_logged


    def login(self, id, email):
        self._id = id
        self._email = email
        self._is_logged = True

    def logout(self):
            self._id = 0
            self._email = ''
            self._is_logged = False
            self._active_wallet = 0

    def sql_injection_replace(self, word):
        disallowed_chars = "\'\"-!\b\n\r\t\\\%\0"
        for char in disallowed_chars:
            word = word.replace(char, '')
        return word