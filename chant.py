from lmlo import lmloCorpus, tenorclef, fullService, fullGenre
import pandas as pd
from collections import defaultdict
from IPython.core.display import display, HTML


decodeSubcorpus = {
    'LF': 'LMLO Feast',
    'LS': 'LMLO Saint',
    'H': 'Humbert Misc',
    'HS': 'Humbert Sanctorale',
    'HT': 'Humber Temporale',
}

decodeService = fullService
decodeGenre = fullGenre
    # '': '',


def recalculate():

    corpus = lmloCorpus()

    # populate chant data frame

    translate_subcorpus = dict()
    translate_subcorpus['Feast'] = 'F'
    translate_subcorpus['Saint'] = 'S'
    translate_subcorpus['Humbert'] = 'H'
    translate_subcorpus['Humbert Sanct.'] = 'HS'
    translate_subcorpus['Humbert Temp.'] = 'HT'

    _data = defaultdict(list)
    for c in corpus.chants:
        _data['corpus'].append('L')
        _subcorpus = c.office.split(']')[0][1:]
        # if _subcorpus == 'Saint':
        #     _subcorpus = 'Sanctorale'
        # if _subcorpus == 'Humber':
        #     _subcorpus = 'Humbert'
        # if _subcorpus == 'Feast':
        #     _subcorpus = 'Feast'
        _data['subcorpus'].append(translate_subcorpus[_subcorpus])
        _data['modus'].append(c.mode)
        _data['Modus'].append(c.mode.lower())
        _data['office'].append(' '.join(c.office.split()[1:]))
        _data['service'].append(c.service)
        _data['Service'].append(fullService[c.Service])
        _data['ordinal'].append(c.index)
        _data['genre'].append(fullGenre[c.genre])
        _data['Genre'].append(fullGenre[c.Genre])
        _data['text'].append(c.fulltext)
        _data['lmloHeader'].append(c.header)
        _data['lmloEncoding'].append(c.lmloEncoding)
        _data['volpiano'].append(c.volpiano)

    pd.DataFrame(_data).to_pickle('chantData.zip')

    # populate note data frame

    _data = defaultdict(list)
    for i_c, c in enumerate(corpus.chants):
        for i_w, w in enumerate(c.words):
            for i_s, s in enumerate(w.syllables):
                for i_n, n in enumerate(s.notes):

                    initial = 0
                    if i_n == 0:
                        initial += 1
                    if i_s == 0:
                        initial *= 2
                    final = 0
                    if i_n == len(s.notes) - 1:
                        final += 1
                    if i_s == len(w.syllables) - 1:
                        final *= 2
                    
                    _data['chantID'].append(i_c)
                    _data['word'].append(i_w)
                    _data['syll'].append(i_s)
                    _data['note'].append(i_n)
                    # _data['text'].append(w.text)
                    _data['boundary_before'].append(initial)
                    _data['boundary_after'].append(final)
                    _data['reg_abs'].append(int(n.letter[0]))
                    _data['pc_abs'].append(n.letter[1])
                    _data['reg_rel'].append(int(n.sd[0]))
                    _data['pc_rel'].append(int(n.sd[1]))

    pd.DataFrame(_data).to_pickle('noteData.zip')

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

def chantData():
    return pd.read_pickle('chantData.zip')

def noteData():
    return pd.read_pickle('noteData.zip')
