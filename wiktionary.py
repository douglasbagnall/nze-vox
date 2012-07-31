#!/usr/bin/python

#import xml.parsers.expat
from xml.etree.cElementTree import iterparse

import bz2
import re
import sys

in_page = False
in_body = False
in_title = False
data = {'term': ''}

NS = "{http://www.mediawiki.org/xml/export-0.7/}"

IPA_re = re.compile("""(?:\{\{a\|(.*)\}\}.*)?
                       \{\{IPA\|([^}]+?)\}
                    """,
                    re.M | re.X)

lang_re = re.compile("lang=[\w.-]+", re.M)


def parse(f):
    data = {}
    for event, e in iterparse(f):#, events=('start', 'end')):
        #if event == 'start':

        #print e.tag
        if e.tag == NS + 'page':
            if len(data) > 1:
                print data
            data = {}
            e.clear()
        elif e.tag == NS + 'title' and ':' not in e.text:
            data['term'] = e.text.encode('utf-8')
        elif e.tag == NS + 'text' and e.text and '{{IPA|' in e.text:
            for m in IPA_re.finditer(e.text):
                accent, pron = m.group(1, 2)
                pronunciations = pron.encode('utf-8').split('|')
                m2 = lang_re.search(pron)
                if m2:
                    data[m2.group(0)] = [p for p in pronunciations if 'lang=' not in p]
                elif not accent:
                    data['default'] = pronunciations
                else:
                    accent = accent.encode('utf-8')
                    accents = accent.split('|')
                    for a in accents:
                        data[a] = pronunciations

f = bz2.BZ2File(sys.argv[1])
parse(f)
