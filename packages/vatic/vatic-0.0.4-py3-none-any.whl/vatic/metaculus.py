import httpx

class User:
    pass

class Question:
    pass

class Metaculus:
    def __init__(self, dest=''):
        self.headers = {}
        self.dest = dest

    def _get(self, endpoint, *args, **kwargs):
        pass

    def _post(self, endpoint, *args, **kwargs):
        pass

    def _get_users(self):
        pass

    def _get_questions(self):
        pass

