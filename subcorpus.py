#!/usr/bin/python
"""Select random exclusive selections of resampled files with approriate metadata.

  ./subcorpus.py <name1> <N1> [[<name2> <N2>] <name3> <N3> ...]

The selections go in corpora/resampled/<name>

For example:

 ./subcorpus.py ahundred 100 twenty 20 more 100

will put 100 utterances in corpora/resampled/ahundred, 20 in
corpora/resampled/twenty, and 100 in corpora/resampled/more. No
utterance will be shared between corpora.
"""

import sys, os
import random
from errno import EEXIST

from os.path import join, isdir

from voxutils.paths import RESAMPLED_16K_DIR, SUBCORPUS_DIR


def copy(src, dest):
    try:
        os.link(src, dest)
    except OSError, e:
        if e.errno != EEXIST:
            raise
    except Exception, e:
        # For windows, just in case
        print e
        import shutil
        shutil.copyfile(src, dest)

def random_subcorpora(corpus, **kwargs):
    """keyword arguments are name1=count1, name2=count2, ...

    Create subdirectories under SUBCORPUS_DIR, named $SUBCORPUS_DIR/name1
    $SUBCORPUS_DIR/name2, etc, each containing count1, count2, etc
    resampled wave files along with a PROMPTS file.
    """
    promptfile = join(corpus, 'etc', 'PROMPTS')
    f = open(promptfile)
    prompts = [x.strip().split(None, 1) for x in f]
    f.close()
    wavmap = {}
    for subdir in ('wav', 'flac'):
        wavdir = join(corpus, subdir)
        if isdir(wavdir):
            for fn in os.listdir(wavdir):
                ID = fn.rsplit('.', 1)[0]
                wavmap[ID] = join(wavdir, fn)

    random.shuffle(prompts)
    for name, count in kwargs.items():
        if count > len(prompts):
            raise IndexError("not enough files! (%s wants %s, %s left)" %
                             (name, count, len(prompts)))

        etcdir = join(SUBCORPUS_DIR, name, 'etc')
        wavdir = join(SUBCORPUS_DIR, name, 'wav')

        try:
            os.makedirs(etcdir)
            os.makedirs(wavdir)
        except OSError, e:
            if e.errno != EEXIST:
                raise

        sample = prompts[:count]
        del prompts[:count]

        transcription = open(join(etcdir, 'transcription'), 'w')
        fileids = open(join(etcdir, 'fileids'), 'w')
        prompt_file = open(join(etcdir, 'PROMPTS'), 'w')
        words = set()
        for ID, text in sample:
            text = text.upper()
            src = wavmap[ID]
            copy(src, join(wavdir, ID + '.wav'))
            print >> prompt_file, "%s %s" % (ID, text)
            print >> fileids, "%s" % (ID,)
            print >> transcription, "<s> %s </s> (%s)" % (text, ID)
            words.update(text.split())

        prompt_file.close()
        fileids.close()
        transcription.close()
        vocab = open(join(etcdir, 'vocab'), 'w')
        for word in sorted(words):
            print >> vocab, word
        vocab.close()


def main():
    if '--help' in sys.argv or '-h' in sys.argv or len(sys.argv) < 1:
        print __doc__
        sys.exit()
    kwargs = {}
    argv = sys.argv[1:]
    while argv:
        k = argv.pop(0)
        kwargs[k] = int(argv.pop(0))

    random_subcorpora(RESAMPLED_16K_DIR, **kwargs)

main()
