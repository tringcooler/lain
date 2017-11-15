#!python2
# coding: utf-8


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


class _lain_chain(object):

    def __init__(self, head, tail, metachain):
        assert isinstance(head, lain_link)
        assert isinstance(tail, lain_link)
        assert isinstance(metachain, _lain_chain)
    
    def isin(self, link):
        pass
    
    def __eq__(self, dest):
        pass
