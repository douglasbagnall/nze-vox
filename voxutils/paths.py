from os.path import dirname, join, abspath

ROOT = dirname(dirname(abspath(__file__)))
DICT = join(ROOT, 'dict')


CORPORA_DIR = join(ROOT, 'corpora')
RESAMPLED_16K_DIR = join(CORPORA_DIR, '16k')
SUBCORPUS_DIR = join(CORPORA_DIR, 'resampled')
IGNORED_CORPORA = ['resampled', '16k']
BASE_CORPORA = ['voxforge', 'wellington', 'hansard']

CORPORA = {x: join(CORPORA_DIR, x) for x in BASE_CORPORA}

CMUDICT = join(DICT, 'cmudict.0.7a')
UNISYN_DICT = join(DICT, 'unisyn-nz.txt')
VOXFORGE_DICT = join(DICT, 'VoxForgeDict')
BEEP_DICT = join(DICT, 'beep', 'beep-1.0')
ESPEAK_DICT = join(DICT, 'espeak-corpus+50k.txt')
