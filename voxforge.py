#!/usr/bin/python

import sys, os
import random

from voxutils.cmudict import lookup_words
from voxutils.resample import convert_one

ROOT = os.path.dirname(os.path.abspath(__file__))
CORPUS = os.path.join(ROOT, 'corpora/voxforge')
RESAMPLED = os.path.join(ROOT, 'corpora/resampled')
CMUDICT = os.path.join(ROOT, 'cmudict.0.7a')

def random_subcorpora(*args):
    """arguments are name1, count1, name2, count2, ...

    Create subdirectories under RESAMPLED, named $RESAMPLED/name1
    $RESAMPLED/name2, etc, each containing count1, count2, etc
    resampled wave files along with a PROMPTS file.
    """
    allfiles = []
    join = os.path.join
    for d in os.listdir(CORPUS):
        promptfile = join(CORPUS, d, 'etc/PROMPTS')
        try:
            f = open(promptfile)
            print f

            prompts = [x.strip().split(None, 1) for x in f]
            f.close()
        except (IOError, OSError), e:
            print promptfile, e
            continue

        wavs = []
        for subdir in ('wav', 'flac'):
            wavdir = join(CORPUS, d, subdir)
            if os.path.exists(wavdir):
                wavs = [join(wavdir, x) for x in os.listdir(wavdir)]
        if not wavs:
            print "no audio for %s" % d
            continue

        pmap = {}
        for pid, text in prompts:
            p = pid.rsplit('/', 1)[1]
            pmap[p] = (pid, text)

        for fn in wavs:
            b = os.path.basename(fn).rsplit('.', 1)[0]
            if b in pmap:
                allfiles.append((fn, b) + pmap[b])


    random.shuffle(allfiles)
    print allfiles, len(allfiles)
    args = list(args)
    while args:
        name = args.pop(0)
        count = args.pop(0)
        if count > len(allfiles):
            raise IndexError("not enough files! (%s wants %s, %s left)" % (name, count, len(allfiles)))

        sample = allfiles[:count]
        del allfiles[:count]

        dirname = join(RESAMPLED, name)
        try:
            os.makedirs(dirname)
        except OSError:
            #probably already exists
            pass
        transcription = open(join(dirname, 'transcription'), 'w')
        fileids = open(join(dirname, 'fileids'), 'w')
        prompts = open(join(dirname, 'PROMPTS'), 'w')
        words = set()
        for fn, p, pid, text in sample:
            pid = pid.replace('/', '-')
            convert_one(fn,
                        join(dirname, pid + '.wav'))
            print >> prompts, "%s %s" % (pid, text)
            print >> fileids, "%s" % (pid,)
            print >> transcription, "<s> %s </s> (%s)" % (text.upper(), pid)
            words.update(text.upper().split())

        prompts.close()
        fileids.close()

        dict_lines, failures = lookup_words(words)
        dic = open(join(dirname, 'words.dic'), 'w')
        for line in sorted(dict_lines):
            print >> dic, line
        dic.close()
        if failures:
            print "unfound words: %s" % (failures,)


#test_convert()

def main():
    args = []
    argv = sys.argv[1:]
    while argv:
        args.append(argv.pop(0))
        args.append(int(argv.pop(0)))


    random_subcorpora(*args)

main()
