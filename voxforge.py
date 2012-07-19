#!/usr/bin/python

import pygst
pygst.require("0.10")
import gst
import sys, os
import random

ROOT = os.path.dirname(os.path.abspath(__file__))
CORPUS = os.path.join(ROOT, 'corpora/voxforge')
RESAMPLED = os.path.join(ROOT, 'corpora/resampled')
CMUDICT = os.path.join(ROOT, 'cmudict.0.7a')

def resample_pipeline(filename, outfilename, rate):
    uri = 'file://' + os.path.abspath(filename)
    s = ("uridecodebin uri=%s "
         "! audioconvert "
         "! audio/x-raw-int,channels=1,width=16,depth=16 "
         "! audioresample "
         "! audio/x-raw-int, rate=%s "
         "! wavenc "
         "! filesink location=%s"
         % (uri, rate, outfilename))
    print s
    pipeline = gst.parse_launch(s)
    return pipeline

def convert_one(filename, outfilename=None, rate=16000):
    if outfilename is None:
        outfilename = '%s-%s.wav' % (filename.rsplit('.', 1)[0], rate)
    pipeline = resample_pipeline(filename, outfilename, rate)
    pipeline.set_state(gst.STATE_PLAYING)


def test_convert():
    import random
    random.seed(1)
    for d in os.listdir(CORPUS):
        for subdir in ('wav', 'flac'):
            wavdir = os.path.join(CORPUS, d, subdir)
            if os.path.exists(wavdir):
                fn = random.choice(os.listdir(wavdir))
                convert_one(os.path.join(wavdir, fn),
                            os.path.join('/tmp', fn))


_cmudict = None
def lookup_words(words):
    global _cmudict
    if _cmudict is None:
        _cmudict = {}
        f = open(CMUDICT)
        for line in f:
            k, v = line.split(None, 1)
            if '(' in k:
                k = k[:k.index('(')]
            values = _cmudict.setdefault(k, [])
            values.append(line.strip())
    lines = []
    failures = set()
    for word in words:
        if word in _cmudict:
            lines.extend(_cmudict[word])
        else:
            failures.add(word)
    return sorted(lines), sorted(failures)

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
