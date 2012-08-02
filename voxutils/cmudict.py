from os.path import dirname, join, abspath

ROOT = dirname(dirname(abspath(__file__)))
CMUDICT = join(ROOT, 'dict', 'cmudict.0.7a')

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
