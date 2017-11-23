#!python2
# coding: utf-8


class lain_link(object):

    def __init__(self):
        self._inst = _lain_link_inst_pool()
        self._parent = _lain_link_inst_pool()
        self._child = _lain_link_inst_pool()


class _lain_link_inst_pool(object):

    def __init__(self):
        self._pool = []

    def foreach(self):
        for i in self._pool:
            yield i

    def __len__(self):
        return len(self._pool)


class _lain_link_inst(object):

    def __init__(self, desc, head, tail):
        assert isinstance(desc, lain_link)
        assert isinstance(head, lain_link)
        assert isinstance(tail, lain_link)
        self._desc = desc
        self._head = head
        self._tail = tail


class _lain_chain(object):

    def __init__(self, root, metachain):
        assert isinstance(root, lain_link)
        assert isinstance(metachain, _lain_chain)
        self._root = root
        self._meta = metachain

    def _traversal_h(self, root = None, ordr = 0):
        if root is None:
            root = self._root
        t_fifo = [('tra', root)]
        while len(t_fifo) > 0:
            token, node = t_fifo.pop(0)
            if token == 'ret':
                yield node
            elif token == 'tra':
                chld = node._child
                chld_len = len(chld)
                while ordr < 0:
                    ordr = ordr + chld_len
                if ordr == 0:
                    yield node
                for cidx, cnode in enumerate(chld.foreach()):
                    t_fifo.append(('tra', cnode))
                    if ordr == cidx + 1:
                        t_fifo.append(('ret', node))
                

    def split(self, metachain):
        pass
    
    def isin(self, link):
        pass
    
    def __eq__(self, dest):
        pass
    
    def __contains__(self, dest):
        pass
    
