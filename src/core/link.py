#!python2
# coding: utf-8

from util import *

LainError = type('LainError', (Exception,), {})

@roprop('inst')
@roprop('parent')
@roprop('child')
class lain_link(object):

    _stamp_index = 0

    def __init__(self):
        self._inst = _lain_link_inst_pool()
        self._parent = _lain_link_inst_pool()
        self._child = _lain_link_inst_pool()
        self._stamp = [0, 0]
        self.stampu = None
        self.stampl = None

    def link_to(self, dest, link):
        assert isinstance(dest, lain_link)
        assert isinstance(link, lain_link)
        _lain_link_inst(link, self, dest)

    def link_from(self, dest, link):
        assert isinstance(dest, lain_link)
        assert isinstance(link, lain_link)
        _lain_link_inst(link, dest, self)

    def stable(self):
        self.upper = None
        self.lower = None

    @lazypropdd
    def upper(self):
        return _lain_chain(self, LainSpreadChain, True)

    @lazypropdd
    def lower(self):
        return _lain_chain(self, LainSpreadChain, False)

    @property
    def stampu(self):
        return self._stamp[0]

    @stampu.setter
    def stampu(self, v):
        self._stamp[0] = lain_link._stamp_index
        lain_link._stamp_index += 1
        if len(self.parent) > 0:
            for l in self.upper.links:
                if l is self:
                    continue
                l.stampu = None

    @property
    def stampl(self):
        return self._stamp[1]

    @stampl.setter
    def stampl(self, v):
        self._stamp[1] = lain_link._stamp_index
        lain_link._stamp_index += 1
        if len(self.parent) > 0:
            for l in self.lower.links:
                if l is self:
                    continue
                l.stampl = None

    def chain(self, metachain = None):
        return _lain_chain(self, metachain, False)

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
        li = head.child.get_inst(desc, head, tail)
        if not li is None:
            assert li == tail.parent.get_inst(desc, head, tail)
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
        print 'link', self.head, '->', self.tail
        self.desc.inst.add(self)
        self.head.child.add(self)
        self.tail.parent.add(self)
        self.head.stampu = None
        self.tail.stampl = None

    def cut(self):
        print 'cut', self.head, '->', self.tail
        self.desc.inst.remove(self)
        self.head.child.remove(self)
        self.tail.parent.remove(self)
        self.head.stampu = None
        self.tail.stampl = None

    def another(self, one):
        if one == self.head:
            return self.tail
        elif one == self.tail:
            return self.head
        else:
            raise ValueError('neither head nor tail')

    def direct(self, one):
        if one == self.head:
            return 'out'
        elif one == self.tail:
            return 'in'
        else:
            raise ValueError('neither head nor tail')

    def __repr__(self):
        return '<link: {:s} inst: {:s} -> {:s}>'.format(
            self.desc, self.head, self.tail)

# WFPOSET: Well-Founded Partially Ordered SET
@neq
@roprop('root')
@roprop('meta')
@roprop('reverse')
class _lain_chain(object):

    def __init__(self, root, metachain = None, reverse = False):
        assert isinstance(root, lain_link)
        assert metachain is None or isinstance(metachain, _lain_chain)
        self._reverse = reverse
        self._root = root
        self._meta = metachain
        self._root_stamp = self._cur_root_stamp()

    def _cur_root_stamp(self):
        if self.reverse:
            rs = (self.root.stampl,)
        else:
            rs = (self.root.stampu,)
        if self.meta:
            rs += self.meta._root_stamp
        return rs

    def _traversal_h(self, root = None, walked = None):
        if self.meta is None:
            return
        if root is None:
            root = self._root
        if walked is None:
            walked = set()
        fifo = [root]
        while len(fifo) > 0:
            node = fifo.pop(0)
            if self.reverse:
                node_succ = node.parent
            else:
                node_succ = node.child
            for li in node_succ.foreach():
                if not li in self.meta:
                    continue
                yield li
                #cnode = li.another(node)
                if self.reverse:
                    assert li.tail == node
                    cnode = li.head
                else:
                    assert li.head == node
                    cnode = li.tail
                if not cnode in walked:
                    walked.add(cnode)
                    fifo.append(cnode)

    def _traversal_v(self, root = None, walked = None):
        if self.meta is None:
            return
        if root is None:
            root = self._root
        if walked is None:
            walked = set()
        if self.reverse:
            root_succ = root.parent
        else:
            root_succ = root.child
        for li in root_succ.foreach():
            if not li in self.meta:
                continue
            yield li
            #cnode = li.another(root)
            if self.reverse:
                assert li.tail == root
                cnode = li.head
            else:
                assert li.head == root
                cnode = li.tail
            if not cnode in walked:
                walked.add(cnode)
                for cli in self._traversal_v(cnode, walked):
                    yield cli

    @lazypropdh
    def links(self):
        print self.root, 'links calc'
        rs = set()
        rs.add(self.root)
        for li in self._traversal_v(self.root, rs):
            pass #do nothing
        self._root_stamp = self._cur_root_stamp()
        return rs

    def links_dirty(self):
        return (self._cur_root_stamp() > self._root_stamp
                or (self.meta and self.meta.links_dirty()))

    def get_links(self, root_out = False):
        rs = self.links.copy()
        if root_out:
            rs.discard(self.root)
        return rs

    def cut(self, metachain = None):
        lis = []
        for li in self._traversal_v(self.root, None):
            lis.append(li)
        for li in lis:
            li.cut()

    def split(self, metachain):
        vlpool = {}
        for li in self._traversal_v(self.root):
            if li in metachain:
                if not li.head in vlpool:
                    vc = vchain()
                    vc.top = li.head
                    vlpool[li.head] = vc
                if not li.tail in vlpool:
                    vc = vchain()
                    vc.top = li.tail
                    vlpool[li.tail] = vc
                vch = vlpool[li.head]
                vct = vlpool[li.tail]
                if self.reverse:
                    if vch.top == li.head:
                        if vct.top == li.head:
                            raise RuntimeError('loop chain', li.head)
                        vch.vlink(vct)
                else:
                    if vct.top == li.tail:
                        if vch.top == li.tail:
                            raise RuntimeError('loop chain', li.tail)
                        vct.vlink(vch)
        chains = {}
        for l in vlpool:
            top = vlpool[l].top
            if not top in chains:
                chains[top] = _lain_chain(top, metachain, self.reverse)
        return chains.values()

    def stable(self):
        for l in self.links:
            l.stable()
    
    @iseq
    def __eq__(self, dest):
        return (isinstance(dest, _lain_chain)
            and type(self) == type(dest)
            and self.root == dest.root
            and self.meta == dest.meta
            and self.reverse == dest.reverse)
    
    def __contains__(self, dest):
        if isinstance(dest, _lain_link_inst):
            link = dest.desc
        elif isinstance(dest, lain_link):
            link = dest
        else:
            #return False
            raise TypeError('checked type should be link')
        return link in self.links

class _lain_any_chain(_lain_chain):
    def split(self, metachain):
        return [self]
    def __contains__(self, dest):
        return True
LainAnyChain = _lain_any_chain(lain_link(), None, False)

class _lain_co_chain(_lain_chain):
    def split(self, metachain):
        rs = super(_lain_co_chain, self).split(metachain)
        return [LainCoChain(ch) for ch in rs]
    def __contains__(self, dest):
        return not super(_lain_co_chain, self).__contains__(dest)

def LainCoChain(ch):
    if ch is None:
        return LainAnyChain
    elif ch is LainAnyChain:
        return None
    elif isinstance(ch, _lain_co_chain):
        return _lain_chain(ch.root, ch.meta, ch.reverse)
    elif isinstance(ch, _lain_chain):
        return _lain_co_chain(ch.root, ch.meta, ch.reverse)
    else:
        raise TypeError('should be a lain chain')

class _lain_isolate_link(lain_link):
    def isolate(self):
        for li in self.child.foreach():
            li.cut()
        for li in self.parent.foreach():
            li.cut()
LainIsolateLink = _lain_isolate_link()
LainSpreadChain = _lain_co_chain(LainIsolateLink, LainAnyChain, False)

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
    #nds[1].link_to(nds[2], tag)
    tagch = tag.chain()
    ch = nds[0].chain(tagch)
    for l in ch.links:
        print 'stable', l,
        if hasattr(l, '_upper'):
                print 'u',
        if hasattr(l, '_lower'):
                print 'l',
        print
    ch.stable()
    chrv = _lain_chain(nds[6], tagch, True)
    print ch.links
    print chrv.links
    nds[1].link_to(nds[2], tag)
    print ch.links
    print chrv.links
    for l in ch.links:
        print 'stable', l,
        if hasattr(l, '_upper'):
                print 'u',
        if hasattr(l, '_lower'):
                print 'l',
        print
    ch.stable()
    nds[3].link_to(nds[4], tag)
    for l in ch.links:
        print 'stable', l,
        if hasattr(l, '_upper'):
                print 'u',
        if hasattr(l, '_lower'):
                print 'l',
        print
    isond = nd('iso')
    isolink = nd('isolink')
    isometa = nd('isometa')
    isolink.link_from(LainIsolateLink, isometa)
    isond.link_to(nds[0], isolink)
    print '===='
    print ch.root.upper.links
    print ch.root.lower.links
    print isond.upper.links
    print isond.lower.links
    #LainSpreadChain.cut()
    LainIsolateLink.isolate()
    print ch.root.upper.links
    print ch.root.lower.links
    print isond.upper.links
    print isond.lower.links
    print '===='
    ndm0 = nd('m0')
    ndm1o = nd('m1o')
    ndm1 = nd('m1')
    ndm2o = nd('m2o')
    ndm2 = nd('m2')
    ndm3o = nd('m3o')
    ndm3 = nd('m3')
    chm0 = ndm0.chain()
    ndm1o.link_to(ndm1, ndm0)
    chm1 = ndm1o.chain(chm0)
    ndm2o.link_to(ndm2, ndm1)
    chm2 = ndm2o.chain(chm1)
    ndm3o.link_to(ndm3, ndm2)
    chm3 = ndm3o.chain(chm2)
    print chm3.links
    chm1.cut()
    print chm3._root_stamp, chm3._cur_root_stamp(), chm3.links_dirty()
    print chm2._root_stamp, chm2._cur_root_stamp(), chm2.links_dirty()
    print chm1._root_stamp, chm1._cur_root_stamp(), chm1.links_dirty()
    print chm1.links
    print chm3._root_stamp, chm3._cur_root_stamp(), chm3.links_dirty()
    print chm2._root_stamp, chm2._cur_root_stamp(), chm2.links_dirty()
    print chm1._root_stamp, chm1._cur_root_stamp(), chm1.links_dirty()
    print chm3.links
    return ch, chrv, isond

if __name__ == '__main__':
    ch, chrv, isond = test()
