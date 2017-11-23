
def roprop(prop):
    def _mod(cls):
        setattr(cls, prop,
                property(lambda self: getattr(self, '_' + prop)))
        return cls
    return _mod

def lazyprop(hndl):
    nm = '_' + hndl.__name__
    def _getter(self):
        if not hasattr(self, nm):
            setattr(self, nm, hndl(self))
        return getattr(self, nm)
    return property(_getter)

def neq(cls):
    def _ne(self, dst):
        return not self == dst
    cls.__ne__ = _ne
    return cls

def iseq(hndl):
    def _iseq(self, dst):
        if self is dst:
            return True
        else:
            return hndl(self, dst)
    return _iseq
