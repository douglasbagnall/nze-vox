from os.path import dirname, join, abspath

ROOT = dirname(dirname(abspath(__file__)))
DICT = join(ROOT, 'dict')


CORPORA_DIR = join(ROOT, 'corpora')
RESAMPLED_DIR = join(CORPORA_DIR, 'resampled')
BASE_CORPORA = ['voxforge', 'wellington']
CORPORA = {x: join(CORPORA_DIR, x) for x in BASE_CORPORA}

CMUDICT = join(DICT, 'cmudict.0.7a')
