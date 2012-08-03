#!/usr/bin/python
from voxutils.resample import convert_one

from errno import EEXIST
import sys, os
from os.path import join

from voxutils.resample import convert_one
from voxutils.paths import CORPORA_DIR, RESAMPLED_DIR

IGNORED_CORPORA = ['resampled', '16k']
BASE_CORPORA = ['voxforge', 'wellington', 'hansard']

CORPORA = {x: os.path.join(CORPORA_DIR, x) for x in BASE_CORPORA}
RESAMPLED_16k = os.path.join(CORPORA_DIR, '16k')


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
            convert_one(fn, newfn)
        print >> prompts, "%s %s" % (pid, transcript)
        print >> fileids, "%s" % (pid,)
        print >> transcription, "<s> %s </s> (%s)" % (transcript, pid)
        words.update(transcript.split())

    prompts.close()
    fileids.close()
    transcription.close()
    vocab = open(join(etc_dir, 'vocab'), 'w')
    for word in sorted(words):
        print >> vocab, word
    vocab.close()


def main(target=RESAMPLED_16k):
    if '--append' in sys.argv:
        sys.argv.remove('--append')
    else:
        for fn in ('fileids', 'PROMPTS', 'transcription', 'vocab'):
            fn = os.path.join(target, 'etc', fn)
            os.rename(fn, fn + '~')

    corpora = sys.argv[1:]
    if corpora == []:
        corpora = [x for x in os.listdir(CORPORA_DIR) if x not in IGNORED_CORPORA]

    for c in corpora:
        d = CORPORA[c]
        resample_corpus(d, target)


main()
