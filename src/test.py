#!/usr/bin/env python

import sys
import os
import resource
import networkx
import argparse
import random
import z3
import ptnet
import pes

def mk_ccnf (n) :
    p = pes.PES ()
    bot = p.add_event ('bot')

    for i in range (n) :
        a = p.add_event ('%da' % i, [bot])
        b = p.add_event ('%db' % i, [bot], [a])

        p.add_event ('%da-succ' % i, [a])
        p.add_event ('%db-succ' % i, [b])

    p.update_minimal ()
    return p


# there is another implementation of this transformation in pes.bp_to_pes()
def unfolding_to_pes (bp) :
    p = pes.PES ()
    evmap = {}

    # create one event in the PES per event in the unfolding
    for e in bp.events :
        evmap[e] = p.add_event (e.label)

    # add presets (causality)
    for e in bp.events :
        pre = set (evmap[ptnet.sgl (c.pre)] for c in e.pre if c.pre)
        for ee in pre :
            evmap[e].pre_add (ee)

    # add conflicts
    for c in bp.conds :
        for e1 in c.post :
            for e2 in c.post :
                if e1 == e2 : continue
                evmap[e1].cfl_add (evmap[e2])
                #print 'cfl e1', e1, 'e2', e2

    p.update_minimal ()
    return p

def test1 () :
    u = ptnet.Unfolding (True)
    #f = open ('/tmp/test.cuf', 'r')
    f = open ('a22.unf.cuf', 'r')
    u.read (f)
    p = unfolding_to_pes (u)
    #p = pes.bp_to_pes (u)

    print '=' * 80
    print 'Unfolding'
    print u

    print '=' * 80
    print 'PES events:'
    print p
    for e in p.events :
        print e

    print '=' * 80
    print 'Maximal configs'
    l = p.iter_max_confs_mx ()
    for mx in l :
        print 'conf', mx
    print len (l), 'max configs'
    

def test2 () :
    assert (len (sys.argv) == 2)

    # unfold with cunf
    cmd = 'cunf -i "%s" -s /tmp/bp.cuf' % sys.argv[1]
    print 'test: cmd "%s"' % cmd
    ret = os.system (cmd)
    print 'test: cunf exit code is', ret
    if ret != 0 : return

    # load the unfolding
    u = ptnet.Unfolding (True)
    f = open ('/tmp/bp.cuf', 'r')
    u.read (f)

    # transform to PES
    p = unfolding_to_pes (u)

    # print unfolding
    print 'test:', '=' * 80
    print 'test: Unfolding'
    print u

    #print 'test:', '=' * 80
    #print 'test: PES events:'
    #print p
    #for e in p.events :
    #    print e

    # enumerate maximal configurations
    print 'test:', '=' * 80
    print 'test: Maximal configs'
    pes.want_dp1 (False)
    l = p.iter_max_confs_mx ()
    avglen = 0
    for mx in l :
        #print 'test: conf', mx
        avglen += len (mx)
    avglen /= 1.0 * len (l)

    print
    print 'test: summary:'
    print 'test: %d events' % len (p.events)
    print 'test: %d conditions' % len (u.conds)
    print 'test: %d max confs' % len (l)
    print 'test: %.2f avg max events in max conf' % avglen

# dump C'15 unfolding and reduced unfolding for argv[1]
def test3 () :
    assert (len (sys.argv) == 2)

    # unfold with cunf
    cmd = 'cunf -i "%s" -s /tmp/bp.cuf' % sys.argv[1]
    print 'test: cmd "%s"' % cmd
    ret = os.system (cmd)
    print 'test: cunf exit code is', ret
    if ret != 0 : return

    # load the unfolding
    u = ptnet.Unfolding (True)
    f = open ('/tmp/bp.cuf', 'r')
    u.read (f)

    # transform to PES
    p = unfolding_to_pes (u)

    # enumerate maximal configurations (classic)
    pes.want_dp1 (False)
    l = p.iter_max_confs_mx ()
    c15 = len (l)
    avglen = 0
    for mx in l :
        #print 'test: conf', mx
        avglen += len (mx)
    avglen /= 1.0 * len (l)

    # enumerate maximal configurations (LFS)
    pes.want_dp1 (True)
    l = p.iter_max_confs_mx ()
    lfs = len (l)

    print 'test: summary:'
    print 'test: %d events' % len (p.events)
    print 'test: %d conditions' % len (u.conds)
    print 'test: %.2f avg max events in max conf (c15)' % avglen
    print 'test: %d max confs c15' % c15
    print 'test: %d max confs lfs' % lfs


# dump results for the CCNF family
def test4 () :

    p = mk_ccnf (7)

    p.write ('/tmp/out.dot', 'dot')

    # enumerate maximal configurations (classic)
    pes.want_dp1 (False)
    l = p.iter_max_confs_mx ()
    c15 = len (l)
    avglen = 0
    for mx in l :
        #print 'test: conf', mx
        avglen += len (mx)
    avglen /= 1.0 * len (l)

    # enumerate maximal configurations (LFS)
    pes.want_dp1 (True)
    l = p.iter_max_confs_mx ()
    lfs = len (l)

    print 'test: summary:'
    print 'test: %d events' % len (p.events)
    print 'test: %.2f avg max events in max conf (c15)' % avglen
    print 'test: %d max confs c15' % c15
    print 'test: %d max confs lfs' % lfs

def main () :
    test4 ()

if __name__ == '__main__' :
    main ()
    sys.exit (0)

# vi:ts=4:sw=4:et:
