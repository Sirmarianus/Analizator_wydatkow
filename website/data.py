class data(object):
    _instance = None
    
    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            cls._id = -1
            cls._email = ''
            cls._is_logged = False
        return cls._instance

    def is_logged(self):
        return self._is_logged


    def login(self, id, email):
        print("id: {}  email: {}".format(id, email))
        self.id = id
        self.email = email
        self._is_logged = True

    def logout(self):
        self.id = -1
        self.email = ''
        self._is_logged = False

         