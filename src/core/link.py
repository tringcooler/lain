
class lain_link(object):

    def __init__(self):
        self._inst_pool = _lain_link_inst_pool()


class _lain_link_inst_pool(object):

    def __init__(self):
        pass


class _lain_link_inst(object):

    def __init__(self, desc):
        assert isinstance(desc, lain_link)
        self._desc = desc
