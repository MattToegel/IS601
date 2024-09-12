class DictToObject:
    def __init__(self, dictionary):
        for key in dictionary:
            setattr(self, key, dictionary[key])
