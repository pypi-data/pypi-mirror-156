class InvalidToken(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return repr(self.msg)

class TokenUnverificable(Exception):
    def __init__(self, msg):
        self.msg = msg 
    def __str__(self):
        return repr(self.msg)