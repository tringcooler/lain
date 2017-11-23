#!python2
# coding: utf-8

LainError = type('LainError', (Exception,), {})

class lain_link(object):

    def __init__(self):
        self._inst = _lain_link_inst_pool()
        self._parent = _lain_link_inst_pool()
        self._child = _lain_link_inst_pool()

    def link_to(self, dest, link):
        assert isinstance(dest, lain_link)
        assert isinstance(link, lain_link)

    def link_from(self, dest, link):
        assert isinstance(dest, lain_link)
        assert isinstance(link, lain_link)


class _lain_link_inst_pool(object):

    def __init__(self):
        self._pool = []

    def foreach(self):
        for i in self._pool:
            yield i

    def __len__(self):
        return len(self._pool)


class _lain_link_inst(object):

    def __new__(self, desc, head, tail):
        assert isinstance(desc, lain_link)
        assert isinstance(head, lain_link)
        assert isinstance(tail, lain_link)
        li = head._child.get(desc, tail)
        if not li is None:
            assert li == tail._child.get(desc, head)
            return li
        else:
            return super(_lain_link_inst, cls).__new__(cls)

    def __init__(self, desc, head, tail):
        self._desc = desc
        self._head = head
        self._tail = tail

    def _link(self):
        self._head._child.add(self)
        self._tail._parent.add(self)

    def another(self, one):
        if one == self._head:
            return self._tail
        elif one == self._tail:
            return self._head
        else:
            raise LainError('neither head nor tail')

class _lain_chain(object):

    def __init__(self, root, metachain):
        assert isinstance(root, lain_link)
        assert isinstance(metachain, _lain_chain)
        self._root = root
        self._meta = metachain

    def _traversal_h(self, root = None):
        if root is None:
            root = self._root
        fifo = [root]
        while len(fifo) > 0:
            node = t_fifo.pop(0)
            yield node
            for cnode in node._child.foreach():
                fifo.append(('tra', cnode))

    def _traversal_v(self, root = None, ordr = 0):
        if root is None:
            root = self._root
        child = root._child
        child_len = len(child)
        while ordr < 0:
            ordr += child_len + 1
        if ordr == 0:
            yield node
        for cidx, cnode in enumerate(child.foreach()):
            for nd in self._traversal_v(cnode, ordr):
                yield nd
            if ordr == cidx + 1:
                yield node

    def split(self, metachain):
        pass
    
    def isin(self, link):
        pass
    
    def __eq__(self, dest):
        pass
    
    def __contains__(self, dest):
        pass
    
def test():
    class nd(lain_link):

        def __init__(self, tag):
            super(nd, self).__init__()
            self.tag = tag

        def __repr__(self):
            return 'nd' + str(tag)

    nds = [nd(i) for i in xrange(7)]
    nds[0]._child

