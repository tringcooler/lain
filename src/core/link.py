#!python2
# coding: utf-8

from util import *

LainError = type('LainError', (Exception,), {})

class lain_link(object):

    def __init__(self):
        self._inst = _lain_link_inst_pool()
        self._parent = _lain_link_inst_pool()
        self._child = _lain_link_inst_pool()

    def link_to(self, dest, link):
        assert isinstance(dest, lain_link)
        assert isinstance(link, lain_link)
        _lain_link_inst(link, self, dest)

    def link_from(self, dest, link):
        assert isinstance(dest, lain_link)
        assert isinstance(link, lain_link)
        _lain_link_inst(link, dest, self)

class _lain_link_inst_pool(object):

    def __init__(self):
        self._pool = []

    def foreach(self):
        for i in self._pool:
            yield i

    def __len__(self):
        return len(self._pool)

    def add(self, dest):
        self._pool.append(dest)

    def remove(self, dest):
        try:
            self._pool.remove(dest)
        except ValueError:
            pass

    def get_inst(self, desc, head, tail):
        for i in self._pool:
            if (i.desc == desc
                and i.head == head
                and i.tail == tail):
                return i
        else:
            return None

@roprop('desc')
@roprop('head')
@roprop('tail')
class _lain_link_inst(object):

    def __new__(cls, desc, head, tail):
        assert isinstance(desc, lain_link)
        assert isinstance(head, lain_link)
        assert isinstance(tail, lain_link)
        li = head._child.get_inst(desc, head, tail)
        if not li is None:
            assert li == tail._parent.get_inst(desc, head, tail)
            #print 'exist'
            return li
        else:
            #print 'new'
            return super(_lain_link_inst, cls).__new__(cls)

    def __init__(self, desc, head, tail):
        self._desc = desc
        self._head = head
        self._tail = tail
        self._link()

    def _link(self):
        self._desc._inst.add(self)
        self._head._child.add(self)
        self._tail._parent.add(self)

    def another(self, one):
        if one == self._head:
            return self._tail
        elif one == self._tail:
            return self._head
        else:
            raise ValueError('neither head nor tail')

    def direct(self, one):
        if one == self._head:
            return 'out'
        elif one == self._tail:
            return 'in'
        else:
            raise ValueError('neither head nor tail')

    def __repr__(self):
        return '<link: {:s} inst: {:s} -> {:s}>'.format(
            self.desc, self.head, self.tail)

@neq
@roprop('root')
@roprop('meta')
class _lain_chain(object):

    def __init__(self, root, metachain):
        assert isinstance(root, lain_link)
        assert not metachain or isinstance(metachain, _lain_chain)
        self._root = root
        self._meta = metachain

    def _traversal_h(self, root = None, walked = None):
        if root is None:
            root = self._root
        if walked is None:
            walked = set()
        fifo = [root]
        while len(fifo) > 0:
            node = fifo.pop(0)
            for li in node._child.foreach():
                yield li
                #cnode = li.another(node)
                assert li.head == node
                cnode = li.tail
                if not cnode in walked:
                    walked.add(cnode)
                    fifo.append(cnode)

    def _traversal_v(self, root = None, walked = None):
        if root is None:
            root = self._root
        if walked is None:
            walked = set()
        for li in root._child.foreach():
            yield li
            #cnode = li.another(root)
            assert li.head == root
            cnode = li.tail
            if not cnode in walked:
                walked.add(cnode)
                for cli in self._traversal_v(cnode, walked):
                    yield cli

    @lazyprop
    def links(self):
        rs = set()
        rs.add(self.root)
        for li in self._traversal_v(self.root, rs):
            pass #do nothing
        return rs

    def split(self, metachain):
        roots = []
        vlpool = {}
        for li in self._traversal_v(self.root):
            if li in self.meta:
                if not li.head in vlpool:
                    vlpool[li.head] = vchain()
                if not li.tail in vlpool:
                    vlpool[li.tail] = vchain()
                vch = vlpool[li.head]
                vct = vlpool[li.tail]
                #vct.
    
    @iseq
    def __eq__(self, dest):
        return (isinstance(dest, _lain_chain)
            and self.root == dest.root
            and self.meta == dest.meta)
    
    def __contains__(self, dest):
        if isinstance(dest, _lain_link_inst):
            link = dest.desc
        elif isinstance(dest, lain_link):
            link = dest
        else:
            #return False
            raise TypeError('checked type should be link')
        return link in self.links
    
def test():
    class nd(lain_link):

        def __init__(self, tag):
            super(nd, self).__init__()
            self.tag = tag

        def __repr__(self):
            return 'nd' + str(self.tag)

    nds = [nd(i) for i in xrange(7)]
    tag = nd('tag')
    nds[0].link_to(nds[1], tag)
    nds[2].link_from(nds[0], tag)
    nds[1].link_to(nds[3], tag)
    nds[4].link_from(nds[1], tag)
    nds[2].link_to(nds[5], tag)
    nds[2].link_to(nds[6], tag)
    nds[1].link_to(nds[2], tag)
    ch = _lain_chain(nds[0], None)
    return ch

if __name__ == '__main__':
    ch = test()
