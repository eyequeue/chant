from lmlo import lmloCorpus, tenorclef, fullService, fullGenre
import pandas as pd
from collections import defaultdict
from IPython.core.display import display, HTML



_corpus = lmloCorpus()

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
    _d['modus'].append(_c.mode)
    _d['office'].append(' '.join(_c.office.split()[1:]))
    _d['service'].append(fullService[_c.service])
    _d['Service'].append(fullService[_c.Service])
    _d['ordinal'].append(_c.index)
    _d['genre'].append(fullGenre[_c.genre])
    _d['Genre'].append(fullGenre[_c.Genre])
    _d['text'].append(_c.fulltext)
    _d['lmloHeader'].append(_c.header)
    _d['lmloEncoding'].append(_c.lmloEncoding)
    _d['volpiano'].append(_c.volpiano)

chantData = pd.DataFrame(_d)

# populate note data frame

_d = defaultdict(list)
for _i_c, _c in enumerate(_corpus.chants):
    for _i_w, _w in enumerate(_c.words):
        for _i_s, _s in enumerate(_w.syllables):
            for _i_n, _n in enumerate(_s.notes):

                _init = 0
                if _i_n == 0:
                    _init += 1
                if _i_s == 0:
                    _init *= 2
                _final = 0
                if _i_n == len(_s.notes) - 1:
                    _final += 1
                if _i_s == len(_w.syllables) - 1:
                    _final *= 2
                
                _d['chantID'].append(_i_c)
                _d['word'].append(_i_w)
                _d['syll'].append(_i_s)
                _d['note'].append(_i_n)
                _d['text'].append(_w.text)
                _d['boundary_before'].append(_init)
                _d['boundary_after'].append(_final)
                _d['register_abs'].append(int(_n.letter[0]))
                _d['letter'].append(_n.letter[1])
                _d['register_rel'].append(int(_n.sd[0]))
                _d['sd'].append(int(_n.sd[1]))

noteData = pd.DataFrame(_d)

def vdisplay(volpiano, size=24, addClef = False, color='black', tenorClef=True):
    if addClef:
        volpiano = '1-'+volpiano
    if tenorClef:
        volpiano = tenorclef(volpiano)

    output = f'<span style="font:{size}px volpiano;color:{color}">{volpiano}</span>'
    display(HTML(output))
    return 

def displayChant(idx):
    
    c = chantData.iloc[idx]

    htmlOut = ''
    htmlOut += f'<span style="font: 12px Roboto"><a href="displaychants?office={c.office}">{c.office}</a> | {fullGenre[c.genre]}'


    fullS = fullService[c.service]
    s = c.service
    htmlOut += f'<table><tr><td style="text-align:left;vertical-align:top">'

    htmlOut += f'<span style="font: 12px Roboto"><span style="font-weight:900;"><a href="displaychants?office={c.office}&service={s}">{fullS}</a>&nbsp;{c.ordinal} </span><br>'

    # htmlOut += f'<span style="font:18px Roboto; font-weight=900"><b>{fullS[0].upper()}</b><span style="font: 12px Roboto">{fullS[1:]}&nbsp;</span><br>'
    htmlOut += f'<span style="font:18px Roboto; font-weight=900"><b><a href="displaychants?genre={c.genre}&mode={c.modus}"><span title={fullGenre[c.genre]}>{c.genre}</span>&#8209;{c.modus}</b></span></a>'
    htmlOut += '</td><td style="text-align:left;vertical-align:top"><span style="font:32px volpiano;">'
    htmlOut += tenorclef(c.volpiano)
    htmlOut += '</span></td></tr></table><br>'
    for i in range(18): htmlOut += '&nbsp;'
    htmlOut += '<span style="font: 12px Merriweather;">{}</span><br><br><br>'.format(c.text.lower())
    display(HTML(htmlOut))
    return

# for _name in dir():
#     if _name.startswith('_'):
#         del globals()[_name]
