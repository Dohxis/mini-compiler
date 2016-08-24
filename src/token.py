class Token(object):

    def __init__(self, type, value):
        self.value = value
        self.type = type

    def __str__(self):
        return "{type}('{value}')".format(
            type = self.type,
            value = self.value
        )

    def __repr__(self):
        return self.__str__()
