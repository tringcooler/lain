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

    def split(self, split_metachain = None, split_chain = None):
        nl = lain_link()
        if not split_metachain is None:
            for li in self.parent.foreach():
                if li in split_metachain:
                    hd = li.head
                    desc = li.desc
                    li.cut()
                    _lain_link_inst(desc, hd, nl)
            for li in self.child.foreach():
                if li in split_metachain:
                    tl = li.tail
                    desc = li.desc
                    li.cut()
                    _lain_link_inst(desc, nl, tl)
        if not split_chain is None:
            split_chain.redesc(self, nl)
        return nl

    def merge_to(self, dest):
        for li in self.parent.foreach():
            hd = li.head
            desc = li.desc
            li.cut()
            _lain_link_inst(desc, hd, dest)
        for li in self.child.foreach():
            tl = li.tail
            desc = li.desc
            li.cut()
            _lain_link_inst(desc, dest, tl)
        for li in self.inst.foreach():
            li.redesc(dest)

    def merge(self, dest):
        return dest.merge_to(self)

    def remove(self):
        for li in self.inst.foreach():
            li.cut()
        for li in self.parent.foreach():
            li.cut()
        for li in self.child.foreach():
            li.cut()

    @property
    def stampu(self):
        return self._stamp[0]

    @stampu.setter
    def stampu(self, v):
        self._stamp[0] = lain_link._stamp_index
        lain_link._stamp_index += 1

    @property
    def stampl(self):
        return self._stamp[1]

    @stampl.setter
    def stampl(self, v):
        self._stamp[1] = lain_link._stamp_index
        lain_link._stamp_index += 1

    def chain(self, metachain = None):
        return _lain_chain(self, metachain, False)

class _lain_link_inst_pool(object):

    def __init__(self):
        self._pool = []

    def foreach(self):
        # reverse order for cut
        for i in xrange(len(self._pool) - 1, -1, -1):
            yield self._pool[i]

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

    def redesc(self, desc):
        if self.desc == desc: return
        print 'redesc', self.head, '->', self.tail, self.desc, 'to', desc
        self.desc.inst.remove(self)
        self._desc = desc
        self.desc.inst.add(self)
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

    def _traversal_h(self, root = None, walked = None, bypass = None):
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
                #cnode = li.another(node)
                if self.reverse:
                    assert li.tail == node
                    cnode = li.head
                else:
                    assert li.head == node
                    cnode = li.tail
                if bypass and cnode in bypass:
                    continue
                yield li
                if not cnode in walked:
                    walked.add(cnode)
                    fifo.append(cnode)

    def _traversal_v(self, root = None, walked = None, bypass = None):
        if root is None:
            root = self._root
        if walked is None:
            walked = set()
        walked.add(root)
        if self.meta is None:
            return
        if self.reverse:
            root_succ = root.parent
        else:
            root_succ = root.child
        for li in root_succ.foreach():
            if not li in self.meta:
                continue
            #cnode = li.another(root)
            if self.reverse:
                assert li.tail == root
                cnode = li.head
            else:
                assert li.head == root
                cnode = li.tail
            if bypass and cnode in bypass:
                continue
            yield li
            if not cnode in walked:
                walked.add(cnode)
                for cli in self._traversal_v(cnode, walked, bypass):
                    yield cli

    def _cur_stamp(self, links = None):
        if links is None:
            links = self._links
        stamp = 0
        for l in links:
            if self.reverse:
                cstamp = l.stampl
            else:
                cstamp = l.stampu
            if cstamp > stamp:
                stamp = cstamp
        rs = (stamp,)
        if self.reverse:
            succ = self.root.parent
        else:
            succ = self.root.child
        if len(succ) > 0 and self.meta:
            rs += self.meta._stamp
        return rs

    @lazypropdh
    def links(self):
        print self.root, 'links calc'
        rs = set()
        self._non_init_links = set()
        self._non_term_links = set()
        for li in self._traversal_v(None, rs):
            self._non_term_links.add(li.head)
            self._non_init_links.add(li.tail)
        self._stamp = self._cur_stamp(rs)
        return rs

    def links_dirty(self):
        if self.reverse:
            succ = self.root.parent
        else:
            succ = self.root.child
        return (self._cur_stamp() > self._stamp
                or (len(succ) > 0 and self.meta and self.meta.links_dirty()))

    @property
    def non_init_links(self):
        _t = self.links
        return self._non_init_links

    @property
    def non_term_links(self):
        _t = self.links
        return self._non_term_links

    @property
    def init_links(self):
        return self.links.difference(self.non_init_links)

    @property
    def term_links(self):
        return self.links.difference(self.non_term_links)

    @property
    def trivial(self):
        return self

    def get_links(self, root_out = False):
        rs = self.links.copy()
        if root_out:
            rs.discard(self.root)
        return rs

    def cut(self, metachain = None):
        lis = []
        for li in self._traversal_v():
            lis.append(li)
        for li in lis:
            li.cut()

    def redesc(self, old, new):
        old = self._get_link_desc(old)
        new = self._get_link_desc(new)
        if old == new: return
        for li in self._traversal_v():
            if li.desc == old:
                li.redesc(new)

    def split(self, metachain):
        cchain = _lain_cluster_chain(metachain, self.reverse)
        cchain.update(self)
        return cchain

    def _chk_dest_valid(self, dest):
        if not isinstance(dest, _lain_chain):
            raise TypeError('unsupported dest type')
        return (self.meta == dest.meta
            and self.reverse == dest.reverse)
    
    @iseq
    def __eq__(self, dest):
        if not self._chk_dest_valid(dest):
            return False
        s = self.trivial
        d = dest.trivial
        if s and d:
            return s.root == d.root
        elif s or d:
            return False
        else:
            return (sorted(s.chains) == sorted(d.chains)
                and sorted(s.neg_chains) == sorted(d.neg_chains))

    def __add__(self, dest):
        if not self._chk_dest_valid(dest):
            raise ValueError(
                'can not merge chains with different meta or direct')
        r = _lain_cluster_chain(self.meta, self.reverse)
        r.update(self)
        r.update(dest)
        return r.trivial or r

    def __sub__(self, dest):
        if not self._chk_dest_valid(dest):
            raise ValueError(
                'can not merge chains with different meta or direct')
        r = _lain_cluster_chain(self.meta, self.reverse)
        r.update(self)
        r.update(dest, True)
        return r.trivial or r

    def __neg__(self):
        r = _lain_cluster_chain(self.meta, self.reverse)
        r.update(self, True)
        return r.trivial or r

    def _get_link_desc(self, link):
        if isinstance(link, _lain_link_inst):
            return link.desc
        elif isinstance(link, lain_link):
            return link
        else:
            raise TypeError('checked type should be link')

    def _contains1(self, dest):
        link = self._get_link_desc(dest)
        return link in self.links

    def _contains_both(self, dests):
        for d in dests:
            if not self._contains1(d):
                return False
        return True
    
    def __contains__(self, dest):
        if hasattr(dest, '__iter__'):
            return self._contains_both(dest)
        else:
            return self._contains1(dest)

@roprop('meta')
@roprop('reverse')
class _lain_cluster_chain(_lain_chain):

    def __init__(self, metachain = None, reverse = False):
        assert metachain is None or isinstance(metachain, _lain_chain)
        self._reverse = reverse
        self._meta = metachain
        self._vlpool = {}
        self._neg_vlpool = {}
        self._chpool = {}
        self._neg_chpool = {}
        self._is_dirty_vlpool = False
        
    def _get_vlpool(self, neg):
        if neg:
            return self._neg_vlpool
        else:
            return self._vlpool

    def _dirty_vlpool(self, neg):
        if neg:
            self.neg_chains = None
        else:
            self.chains = None
        self._is_dirty_vlpool = True

    def update(self, chain, neg = False):
        if isinstance(chain, _lain_cluster_chain):
            for ch in chain.chains:
                self._update_chain(ch, neg)
            for ch in chain.neg_chains:
                self._update_chain(ch, not neg)
        else:
            self._update_chain(chain, neg)

    def _update_chain(self, chain, neg):
        _isoroot = True
        for li in chain._traversal_v():
            _isoroot = False
            self._update_li(li, neg)
        if _isoroot:
            self._update_isolink(chain.root, neg)

    def _update_isolink(self, link, neg):
        vlpool = self._get_vlpool(neg)
        if link and not link in vlpool:
            vc = vchain()
            vc.top = link
            vlpool[link] = vc
            self._dirty_vlpool(neg)

    def _update_li(self, li, neg):
        if not li in self.meta:
            return
        vlpool = self._get_vlpool(neg)
        if not li.head in vlpool:
            vc = vchain()
            vc.top = li.head
            vlpool[li.head] = vc
            self._dirty_vlpool(neg)
        if not li.tail in vlpool:
            vc = vchain()
            vc.top = li.tail
            vlpool[li.tail] = vc
            self._dirty_vlpool(neg)
        vch = vlpool[li.head]
        vct = vlpool[li.tail]
        if self.reverse:
            if vch.top == li.head:
                if vct.top == li.head:
                    raise RuntimeError('loop chain', li.head)
                vch.vlink(vct)
                self._dirty_vlpool(neg)
        else:
            if vct.top == li.tail:
                if vch.top == li.tail:
                    raise RuntimeError('loop chain', li.tail)
                vct.vlink(vch)
                self._dirty_vlpool(neg)

    def _get_chains(self, neg):
        print 'calc vlpool -> chains'
        vlpool = self._get_vlpool(neg)
        if neg:
            chains = self._neg_chpool
        else:
            chains = self._chpool
        new_chains = {}
        for l in vlpool:
            top = vlpool[l].top
            if not top in chains:
                new_chains[top] = _lain_chain(top, self.meta, self.reverse)
            else:
                new_chains[top] = chains[top]
        if neg:
            self._neg_chpool = new_chains
        else:
            self._chpool = new_chains
        self._is_dirty_vlpool = False
        return new_chains.values()
        
    @lazypropds
    def chains(self):
        return self._get_chains(False)

    @lazypropds
    def neg_chains(self):
        return self._get_chains(True)

    @lazypropdh
    def trivial(self):
        if not len(self.chains) == 1:
            return None
        och = self.chains[0]
        och.links #refresh chain links dirty flag
        for chain in self.neg_chains:
            if och.links.intersection(chain.links):
                return None
        return och

    def trivial_dirty(self):
        return self.links_dirty()

    def _traversal_h(self, root = None, walked = None, bypass = None):
        return self._traversal_x(root, walked, bypass, False)

    def _traversal_v(self, root = None, walked = None, bypass = None):
        return self._traversal_x(root, walked, bypass, True)
    
    def _traversal_x(self, root, walked, bypass, vorh):
        if self.meta is None:
            return
        if walked is None:
            walked = set()
        if bypass is None:
            bypass = set()
        for chain in self.neg_chains:
            bypass.update(chain.links)
        for chain in self.chains:
            chain.links #refresh chain links dirty flag
            if vorh:
                _trv = chain._traversal_v
            else:
                _trv = chain._traversal_h
            if root and root in chain.links:
                for li in _trv(root, walked, bypass):
                    yield li
                return
            elif root is None:
                for li in _trv(chain.root, walked, bypass):
                    yield li

    def links_dirty(self):
        if self._is_dirty_vlpool:
            return True
        for chain in self.chains:
            if chain.links_dirty():
                return True
        for chain in self.neg_chains:
            if chain.links_dirty():
                return True
        return False

    def _contains_both(self, dests):
        if not super(_lain_cluster_chain, self)._contains_both(dests):
            return False
        for chain in self.chains:
            if chain._contains_both(dests):
                return True
        return False

    @property
    def root(self):
        return None

    def _cur_stamp(self, links = None):
        return None

class _lain_any_chain(_lain_chain):
    def split(self, metachain):
        return self
    def __contains__(self, dest):
        return True
LainAnyChain = _lain_any_chain(lain_link(), None, False)

class _lain_co_chain(_lain_chain):
    def split(self, metachain):
        rs = super(_lain_co_chain, self).split(metachain)
        return LainCoChain(rs)
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
    elif isinstance(ch, _lain_cluster_chain):
        raise NotImplementedError('CoCC')
    else:
        raise TypeError('should be a lain chain')

@neq
@roprop('sroot')
@roprop('droot')
@roprop('meta')
class _lain_cross(object):

    def __init__(self, sroot, droot, metacross = None):
        assert isinstance(sroot, lain_link)
        assert isinstance(droot, lain_link)
        assert metacross is None or isinstance(metacross, _lain_cross)
        self._sroot = sroot
        self._droot = droot
        self._meta = metacross


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
    chrv = _lain_chain(nds[6], tagch, True)
    print ch.links
    print chrv.links
    nds[1].link_to(nds[2], tag)
    print ch.links
    print chrv.links
    nds[3].link_to(nds[4], tag)
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
    print chm3._stamp, chm3._cur_stamp(), chm3.links_dirty()
    print chm2._stamp, chm2._cur_stamp(), chm2.links_dirty()
    print chm1._stamp, chm1._cur_stamp(), chm1.links_dirty()
    print chm1.links
    print chm3._stamp, chm3._cur_stamp(), chm3.links_dirty()
    print chm2._stamp, chm2._cur_stamp(), chm2.links_dirty()
    print chm1._stamp, chm1._cur_stamp(), chm1.links_dirty()
    print chm3.links
    print '===='
    print [i for i in nds[1].inst.foreach()]
    print [i for i in nds[1].parent.foreach()]
    print [i for i in nds[1].child.foreach()]
    print [i for i in nds[2].inst.foreach()]
    print [i for i in nds[2].parent.foreach()]
    print [i for i in nds[2].child.foreach()]
    nds[1].merge(nds[2])
    print ch.links
    print [i for i in nds[1].inst.foreach()]
    print [i for i in nds[1].parent.foreach()]
    print [i for i in nds[1].child.foreach()]
    print [i for i in nds[2].inst.foreach()]
    print [i for i in nds[2].parent.foreach()]
    print [i for i in nds[2].child.foreach()]
    print '===='
    nds = [nd(i) for i in xrange(7)]
    tag2 = nd('tag2')
    tag3 = nd('tag3')
    mtag = nd('mtag')
    tag.link_to(tag2, mtag)
    tag2.link_to(tag3, mtag)
    mtagch = mtag.chain()
    tagch1 = tag.chain(mtagch)
    tagch2 = tag2.chain(mtagch)
    tagch3 = tag3.chain(mtagch)
    nds[0].link_to(nds[1], tag)
    nds[0].link_to(nds[2], tag)
    nds[1].link_to(nds[3], tag2)
    nds[2].link_to(nds[3], tag2)
    nds[3].link_to(nds[4], tag2)
    nds[3].link_to(nds[5], tag2)
    nds[4].link_to(nds[6], tag3)
    nds[5].link_to(nds[6], tag3)
    ch1 = nds[0].chain(tagch1)
    ch2 = nds[0].chain(tagch2)
    ch2s = ch1.split(tagch2)
    print [i.root for i in ch2s.chains]
    vlpch2s = ch2s._vlpool
    print [(k, vlpch2s[k].top) for k in vlpch2s]
    ch2s = ch1.split(tagch2)
    ch2s.update(nds[6].chain(), True)
    print [i.root for i in ch2s.chains]
    print [i.root for i in ch2s.neg_chains]
    print [i for i in ch2s._traversal_v()]
    ch2sr = ch1.split(tagch3)
    for c in ch2sr.chains:
        print 'update neg', c.root
        ch2s.update(c, True)
    print [i.root for i in ch2s.chains]
    print [i.root for i in ch2s.neg_chains]
    print [i for i in ch2s._traversal_v()]
    ch1s = ch1.split(tagch1)
    print ch1s == ch1
    print ch1s == ch1
    ch2add = ch2 + ch2s
    print ch2add.links
    print ch2add.chains[0] == ch2s.chains[0]
    print ch2add.chains[2] == ch2s.chains[1]
    print ch2add.chains[1] == ch2
    print '===='
    nds = [nd(i) for i in xrange(10)]
    nds[0].link_to(nds[1], tag)
    nds[0].link_to(nds[2], tag)
    nds[1].link_to(nds[3], tag2)
    nds[1].link_to(nds[4], tag2)
    nds[2].link_to(nds[4], tag2)
    nds[2].link_to(nds[5], tag2)
    nds[3].link_to(nds[6], tag2)
    nds[4].link_to(nds[7], tag2)
    nds[4].link_to(nds[8], tag2)
    nds[5].link_to(nds[9], tag2)
    ch1 = nds[0].chain(tagch1)
    ch2 = ch1.split(tagch2)
    print [nds[6], nds[7], nds[8], nds[9]] in ch1
    print [nds[6], nds[7], nds[8], nds[9]] in ch2
    print [nds[6], nds[7]] in ch2
    print [nds[7], nds[8]] in ch2
    print [nds[8], nds[9]] in ch2
    print [nds[6], nds[9]] in ch2
    return nds, ch1, ch2, tagch1

if __name__ == '__main__':
    nds, ch1, ch2, tagch1 = test()
