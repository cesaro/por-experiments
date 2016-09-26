
from configuration import *

nonvis = set ()
avg_c_size = 0

__want_dp1 = False

def want_dp1 (w) :
    global __want_dp1
    __want_dp1 = w

def dp1_ignore_c (pes, c, e) :
    global nonvis

    # if e not visisted, then Yes!!
    if e in nonvis : return True

    # ignore c
    for ep in nonvis :
        if pes.in_caus (e, ep) : return True
    return False

def dp1_exact (pes, c, e) :
    global nonvis

    # if e not visisted, then Yes!!
    if e in nonvis : return True

    # get cex(c)
    cex = c.cex ()

    # ignore c
    for ep in nonvis :
        # skip events not in the inverted cone
        if not pes.in_caus (e, ep) : continue
        found = False
        for ex in cex :
            if pes.in_caus (ex, ep) :
                found = True
                break
        if not found : return True
    return False

def dp1 (pes, c, e) :
    global __want_dp1
    if not __want_dp1 : return True
    ret = dp1_ignore_c (pes, c, e)
    #print 'emc: dp1 %s, %s' % (e, ret)
    return ret

def enum_max_conf (pes, c, d, a, enum, want=0) :
    global nonvis
    global avg_c_size

    # implementation of the CONCUR'15 algorithm on a fully constructed PES

    # c is a Configuration object
    # d is a list
    # a is mark obtained by pes.new_mark(), or -1

    # invariants
    # - all events in d are enabled at c (none is in cex(c))

    if len (c.events) == 0 and len (d) == 0 :
        print 'emc: first call, initializing nonvis; want_dp1', __want_dp1
        nonvis = set (pes.events)
        avg_c_size = 0

    #print 'emc:', '=' * 50
    #print 'emc: call: c %s d %s a %s nonvis %d' % (list(c.events), d, a, len (nonvis))
    #print 'emc: call: c %d d %d a %s nv %d' % (len (c.events), len (d), a, len (nonvis))

    # if maximal configuration, backtrack
    #en = c.enabled ()
    en = [e for e in c.enabled () if (a > 1 or dp1 (pes, c, e))] # we do J until the end
    if len (en) == 0 :
        #print 'emc: MAX:', c
        #print 'emc: max!'
        #print 'emc: max! c', len (c.events), 'en', len (c.enabled ()), 'nv', len (nonvis)
        if want == 0 :
            enum.append (list (c.maximal ()))
        elif want == 1 :
            enum.append (c)
        avg_c_size += len (c.events)
        return avg_c_size

    # pick an enabled event, possibly marked by a
    if a == -1 :
        e = next (iter (en))
    else :
        #print 'xxx', en, [ee.m for ee in en]
        l = [ee for ee in en if ee.m == a]
        if len (l) >= 1 :
            e = l[0]
        else :
            e = next (iter (en))
            a = -1 # optimization
    #print 'emc: picked %s en %s a %d' % (repr (e), c.enabled (), a)

    # left subtree, we create copies of c and d, so the recursive call is
    # free to handle them as it wants
    cc = c.clone ()
    cc.add (e)
    dd = __enum_max_conf_clean_d (pes, cc, d, e)
    nonvis.discard (e)
    enum_max_conf (pes, cc, dd, a, enum, want)

    # compute the alternatives, labelling J by the mark a (if != -1)
    d.append (e)
    a = __enum_max_conf_alt (pes, c, d)

    # right subtree
    if a != -1 :
        #print 'emc: found alternative, exploring right subtree'
        enum_max_conf (pes, c, d, a, enum, want)
    #print 'emc: ret'
    return avg_c_size

def __enum_max_conf_clean_d (pes, c, d, last) :
    # every event in d is ether enabled at c or in immediate conflict with
    # last; remove from d those in conflict
    return [e for e in d if e not in last.cfl]

def __enum_max_conf_alt (pes, c, d) :
    # mark all events in conflict with at least one event in c
    #print 'alt: c %s d %s' % (c.events, d)
    m = pes.new_mark ()
    l = []
    for e in c : l.extend (e.cfl)
    for e in pes.iter_causal_future (l) : e.m = m

    # if an event is marked with m, it cannot be be contained in any
    # alternative, now compute the clauses, one per event in d
    clauses = [[ep for ep in e.cfl if ep.m != m] for e in d]
    comb = Comb (pes, clauses)
    sol = comb.explore ()
    #print 'alt: c %s d %s alt %s' % (c.events, d, sol)

    # if we got a solution, mark it and return the mark
    if sol == None : return -1
    m = pes.new_mark ()
    pes.mark_causal_past (m, sol) # very suboptimal, don't need to enter in c ...
    return m

class Comb :
    def __init__ (self, pes, clauses) :
        self.pes = pes
        self.comb = [Comb.Watchlist (ls) for ls in clauses]
        self.size = len (clauses)
        self.top = 0

        #print 'comb: new comb, size', self.size
        #for wl in self.comb :
        #    print 'comb:  ', wl

    def explore (self) :
        # a comb with 0 spikes has a trivial empty solution
        if self.size == 0 : return []
        # if one spike is empty, there is no solution
        if 0 in [w.size for w in self.comb] : return None
        # if all spikes contain at least one event, we need to search
        while True :
            if self.comb[self.top].empty () :
                #print 'comb: top %d is empty' % (self.top)
                self.top -= 1
                if self.top == -1 : return None
                #print 'comb: top %d advance' % (self.top)
                self.comb[self.top].advance ()
                #print 'comb: top %d %s' % (self.top, self.comb[self.top])
            else :
                #print 'comb: top %d is not empty' % (self.top)
                if self.propagate () == self.size :
                    #print 'comb: top %d propagation ok:' % (self.top)
                    #for wl in self.comb : print 'comb:  ', wl
                    #print 'comb: top %d advance' % (self.top)
                    self.top += 1
                    if self.top == self.size : break
                else :
                    #print 'comb: top %d propagation not ok, advancing top wl:' % (self.top)
                    self.comb[self.top].advance ()
                    #print 'comb: %s' % (self.comb[self.top])
                    # reset previous propagations
                    for i in range (self.top + 1, self.size) :
                        self.comb[i].reset ()
                        #print 'comb: top %d reseted %d %s' % (self.top, i, self.comb[i])

        # if we get here, we got a solution
        return [self.comb[i].get() for i in range (self.size)]

    def propagate (self) :
        # forward propagates the effect of the last decision
        # (comb[top].current), ie, to the Watchlists between top+1 and size-1
        # returns size if no Watchlist becomes empty, or the index (in that
        # range) of the first Watchlist that becomes empty
        last = self.comb[self.top].get ()
        #print 'comb: propagate: top %d last %s' % (self.top, repr (last))
        for i in range (self.top + 1, self.size) :
            #print 'comb: propagate: i', i
            if self.pes.in_cfl (last, self.comb[i].get()) :
                while True :
                    self.comb[i].advance ()
                    if self.comb[i].empty () : return i
                    e = self.comb[i].get ()
                    found = False
                    for j in range (self.top + 1) :
                        if self.pes.in_cfl (e, self.comb[j].get ()) :
                            found = True
                            break
                    if not found : break
        return self.size

    class Watchlist :
        def __init__ (self, ls) :
            self.ls = ls
            self.size = len (ls)
            self.current = 0
            self.remain = self.size
        def empty (self) :
            return self.remain == 0
        def reset (self) :
            # better than start = current (with regard to conflicts...)
            self.current = 0
            self.remain = self.size
        def advance (self) :
            # advance the current position by one
            self.current = (self.current + 1) % self.size
            self.remain -= 1
        def get (self) :
            return self.ls[self.current]
        def __str__ (self) :
            return 'wl cur %d rem %d (%s) ls %s' % \
                    (self.current, self.remain,
                    repr (self.ls[self.current]) if self.size else "",
                    self.ls)

# vi:ts=4:sw=4:et:
