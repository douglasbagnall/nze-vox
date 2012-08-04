#!/usr/bin/python
"""Resample and collate corpora, storing the result in corpora/16k

./resample-all.py [--force] [--append] [--help] [[<corpus>]...]

If corpora are listed on the command line, only those subdirectories
of ./corpora/ will be used. The default is to use all corpora except
the already resampled ones.

If --force is given, already resampled files will be overwritten.

--apend adds to the existing metadata rather than writing it afresh.
"""
from voxutils.resample import convert_one

from errno import EEXIST
import sys, os
from os.path import join

from voxutils.resample import convert_one, gst_init
from voxutils.paths import CORPORA_DIR, RESAMPLED_16K_DIR, IGNORED_CORPORA

def log(*msgs):
    for m in msgs:
        print >> sys.stderr, m

def read_prompt_file(path):
    ids = []
    f = open(path)
    for line in f:
        fn, transcript = line.strip().split(None, 1)
        if '/' in fn:
            base_id = fn.rsplit('/', 1)[1]
        else:
            base_id = fn
        uid = fn.replace('/', '-')
        ids.append([base_id, fn, uid, transcript])
    f.close()
    return ids

def prompt_file_gen(corpus):
    allfiles = []
    for root, dirs, files in os.walk(corpus, followlinks=True):
        if 'etc' in dirs:
            try:
                ids = read_prompt_file(join(root, 'etc', 'PROMPTS'))
                dirs.remove('etc')
            except (IOError, OSError), e:
                log(e)
                continue
        elif  'PROMPTS' in files:
            ids = read_prompt_file(join(root, 'PROMPTS'))
        else:
            ids = []
        for subdir in ('wav', 'flac'):
            if subdir in dirs:
                dirs.remove(subdir)
                wavdir = join(root, subdir)
                wavfiles = {x.rsplit('.', 1)[0] : x for x in os.listdir(wavdir)}
                for x in ids:
                    base_id = x[0]
                    if base_id in wavfiles:
                        x.append(join(wavdir, wavfiles[base_id]))
                        allfiles.append(x)

    for x in allfiles:
        yield x


def resample_corpus(corpus_dir, resample_dir, force=False):
    etc_dir = join(resample_dir, 'etc')
    wav_dir = join(resample_dir, 'wav')
    try:
        os.makedirs(etc_dir)
        os.makedirs(wav_dir)
    except OSError, e:
        if e.errno != EEXIST:
            raise

    transcription = open(join(etc_dir, 'transcription'), 'a')
    fileids = open(join(etc_dir, 'fileids'), 'a')
    prompts = open(join(etc_dir, 'PROMPTS'), 'a')
    words = set()

    for base_id, fn, pid, transcript, wavfile in prompt_file_gen(corpus_dir):
        pid = pid.replace('/', '-')
        transcript = transcript.upper()
        newfn = os.path.join(wav_dir, pid + '.wav')
        if force or not os.path.exists(newfn):
            convert_one(wavfile, newfn)
        print >> prompts, "%s %s" % (pid, transcript)
        print >> fileids, "%s" % (pid,)
        print >> transcription, "<s> %s </s> (%s)" % (transcript, pid)
        words.update(transcript.split())

    prompts.close()
    fileids.close()
    transcription.close()
    vocab = open(join(etc_dir, 'vocab'), 'a')
    for word in sorted(words):
        print >> vocab, word
    vocab.close()


def main(target=RESAMPLED_16K_DIR):
    if '--help' in sys.argv or '-h' in sys.argv:
        print __doc__
        sys.exit()
    if '--force' in sys.argv:
        sys.argv.remove('--force')
        force = True
    else:
        force = False
    if '--append' in sys.argv:
        sys.argv.remove('--append')
    else:
        for fn in ('fileids', 'PROMPTS', 'transcription', 'vocab'):
            fn = os.path.join(target, 'etc', fn)
            try:
                os.rename(fn, fn + '~')
            except OSError, e:
                log("%s does not exist" % fn)

    gst_init()
    corpora = sys.argv[1:]
    if corpora == []:
        corpora = [x for x in os.listdir(CORPORA_DIR) if x not in IGNORED_CORPORA]

    for c in corpora:
        d = join(CORPORA_DIR, c)
        resample_corpus(d, target, force=force)


main()
