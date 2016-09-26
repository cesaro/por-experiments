#!/usr/bin/env python

import sys
import ptnet

if __name__ == '__main__' :
    n = ptnet.Unfolding (True)
    n.read (sys.stdin, 'cuf')
    n.write (sys.stdout, 'pnml')

# vi:ts=4:sw=4:et:
