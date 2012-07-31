#!/usr/bin/python
import sys

def read(f):
    for line in f:
        d = eval(line)
        yield d

def lexicon(f, priorities):
    for d in read(f):
        if 'term' not in d:
            print >> sys.stderr, d
            continue
        term = d['term']
        for p in priorities:
            if p in d:
                pron = d[p]
                break
        else:
            if 'default' in d:
                pron = d['default']
            else:
                for k, v in d.iteritems():
                    if k != 'term':
                        pron = v
                        break

        p = "  ".join(pron)
        print "%-20s %20s" % (term, p)


f = open(sys.argv[1])
lexicon(f, ['NZ', 'AU', 'RP', 'UK', 'US'])
