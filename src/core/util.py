
def roprop(prop):
    def _mod(cls):
        setattr(cls, prop,
                property(lambda self: getattr(self, '_' + prop)))
        return cls
    return _mod
