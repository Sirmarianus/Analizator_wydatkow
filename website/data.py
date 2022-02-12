class data(object):
    _instance = None
    
    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            cls._id = -1
            cls._email = ''
            cls._is_logged = False
            cls._active_wallet = 1
        return cls._instance

    def is_logged(self):
        return self._is_logged


    def login(self, id, email):
        self._id = id
        self._email = email
        self._is_logged = True

    def logout(self):
        self._id = -1
        self._email = ''
        self._is_logged = False

         