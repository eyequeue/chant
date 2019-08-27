import lmlo
import pandas as pd
from collections import defaultdict

_corpus = lmlo.lmloCorpus()

# populate chant data frame

_d = defaultdict(list)
for _c in _corpus.chants:
    _d['corpus'].append('lmlo')
    _subcorpus = _c.office.split()[0][1:-1]
    if _subcorpus == 'Saint':
        _subcorpus = 'Sanctorale'
    if _subcorpus == 'Humber':
        _subcorpus = 'Humbert'
    if _subcorpus == 'Feast':
        _subcorpus = 'Feast'
    _d['subcorpus'].append(_subcorpus)
    _d['mode'].append(_c.mode)
    _d['office'].append(' '.join(_c.office.split()[1:]))
    _d['service'].append(_c.service)
    _d['index'].append(_c.index)
    _d['genre'].append(_c.genre)
    _d['text'].append(_c.fulltext)
    _d['lmloHeader'].append(_c.header)
    _d['lmloEncoding'].append(_c.lmloEncoding)

chantData = pd.DataFrame(_d)

# populate note data frame

_d = defaultdict(list)
for _i_c, _c in enumerate(_corpus.chants):
    for _i_w, _w in enumerate(_c.words):
        for _i_s, _s in enumerate(_w.syllables):
            for _i_n, _n in enumerate(_s.notes):

                _syll_init = False
                if _i_n == 0:
                    _syll_init = True
                _syll_final = False
                if _i_n == len(_s.notes) - 1:
                    _syll_final = True
                _word_init = False
                if _i_s == 0 and _syll_init:
                    _word_init = True
                _word_final = False
                if _i_s == len(_w.syllables) - 1 and _syll_final:
                    _word_final = True
                
                _d['chantID'].append(_i_c)
                _d['word'].append(_i_w)
                _d['syll'].append(_i_s)
                _d['note'].append(_i_n)
                _d['word_init'].append(_word_init)
                _d['syll_init'].append(_syll_init)
                _d['text'].append(_w.text)
                _d['syll_final'].append(_syll_final)
                _d['word_final'].append(_word_final)
                _d['letter'].append(_n.letter)
                _d['sd'].append(_n.sd)

noteData = pd.DataFrame(_d)

for _name in dir():
    if _name.startswith('_'):
        del globals()[_name]
