#!/usr/bin/python
# -*- coding: utf-8 -*-
"""

called thus:

python regularise-corpora-prompts.py some-prefix/here- < in_file > PROMPTS

Turns files in this form:

0003 What reports has he received on progress in lifting New Zealand’s household savings

0007 which shows that net household savings in that year were naught point
two percent of


into something like this

some-prefix/here-0003 WHAT REPORTS HAS HE RECEIVED ON PROGRESS IN LIFTING NEW ZEALAND'S HOUSEHOLD SAVINGS
some-prefix/here-0007 WHICH SHOWS THAT NET HOUSEHOLD SAVINGS IN THAT YEAR WERE NAUGHT POINT TWO PERCENT OF
"""


import os, sys
import re


gone_re = re.compile(r"[^ \w'-]")

def clean_up_utterance(text):
    text = text.replace("’", "'").upper()
    text = gone_re.sub('', text)
    text = ' '.join(text.split())
    return text

def get_utterances_gen(f):
    utt_id = None
    utterance = ''
    for line in f:
        line = line.strip()
        if not line:
            if utt_id:
                yield utt_id, utterance
            utt_id = None
            utterance = ''
        elif utt_id is None:
            bits = line.split(None, 1)
            utt_id = bits[0]
            if len(bits) == 2:
                utterance = clean_up_utterance(bits[1])
            else:
                utterance = ''

        else: # a continuation
            utterance += " " + clean_up_utterance(line)

    if utt_id:
        yield utt_id, utterance






def main():
    prefix = sys.argv[1]
    for uid, utterance in get_utterances_gen(sys.stdin):
        print "%s%s  %s" % (prefix, uid, utterance)





main()
