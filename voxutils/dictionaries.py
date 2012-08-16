from voxutils import paths

DICTS = {
    'cmudict':  (paths.CMUDICT, 1, {}),
    'beep':     (paths.BEEP_DICT, 1, {}),
    'unisyn':   (paths.UNISYN_DICT, 1, {}),
    'voxforge': (paths.VOXFORGE_DICT, 2, {}),
    'espeak':   (paths.ESPEAK_DICT, 1, {}),
}

def get_dict(name):
    path, field, d = DICTS[name]
    if d == {}:
        f = open(path)
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            bits = line.split(None, field)
            k = bits[0]
            v = bits[field]
            if '(' in k:
                k = k[:k.index('(')]
            values = d.setdefault(k, [])
            values.append("%s %s" % (k, v))
    DICTS[name] = (path, field, d)
    return d

def lookup_words(words, dictname='cmudict'):
    lut = get_dict(dictname)
    lines = []
    failures = set()
    for word in words:
        if word in lut:
            lines.extend(lut[word])
        else:
            failures.add(word)
    return sorted(lines), sorted(failures)


