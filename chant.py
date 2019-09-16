from lmlo import lmloCorpus, tenorclef, fullService, fullGenre
import pandas as pd
import numpy
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


def _recalculate():

    corpus = lmloCorpus()

    # populate chant data frame

    translate_subcorpus = dict()
    translate_subcorpus['Feast'] = 'LF'
    translate_subcorpus['Saint'] = 'LS'
    translate_subcorpus['Humbert'] = 'H'
    translate_subcorpus['Humbert Sanct.'] = 'HS'
    translate_subcorpus['Humbert Temp.'] = 'HT'

    _data = defaultdict(list)
    for i, c in enumerate(corpus.chants):
        _data['chantID'].append(i)
        _data['corpus'].append('L')
        _subcorpus = c.office.split(']')[0][1:]
        # if _subcorpus == 'Saint':
        #     _subcorpus = 'Sanctorale'
        # if _subcorpus == 'Humber':
        #     _subcorpus = 'Humbert'
        # if _subcorpus == 'Feast':
        #     _subcorpus = 'Feast'
        _data['subcorpus'].append(translate_subcorpus[_subcorpus])
        _data['Modus'].append(c.mode)
        _data['modus'].append(c.mode.lower())
        if c.mode[0] in ['1','2']:
            _data['maneria'].append('protus')
        elif c.mode[0] in ['3','4']:
            _data['maneria'].append('deuterus')
        elif c.mode[0] in ['5','6']:
            _data['maneria'].append('tritus')
        elif c.mode[0] in ['7','8']:
            _data['maneria'].append('tetrardus')
        else:
            _data['maneria'].append('unknown')
        if c.mode[1] == c.mode[1].upper():
            _data['ambitus'].append('excessive')
        elif c.mode[0] in ['1','3','5','7']:
            _data['ambitus'].append('authentic')
        elif c.mode[0] in ['2','4','6','8']:
            _data['ambitus'].append('plagal')
        else:
            _data['ambitus'].append('unknown')


        _data['office'].append(' '.join(c.office.split()[1:]))

        # switching the names Service/service and Genre/genre from lmlo module
        # for consistency with Modus/modus: capital is the more granular grouping

        _data['Service'].append(c.service)
        _data['service'].append(c.Service)
        _data['ordinal'].append(c.index)
        _data['Genre'].append(c.genre)
        _data['genre'].append(c.Genre)
        _data['text'].append(c.fulltext)
        # _data['lmloHeader'].append(c.header)
        # _data['lmloEncoding'].append(c.lmloEncoding)
        _data['volpiano'].append(c.volpiano)

    pd.DataFrame(_data).to_pickle('chantData.zip')

    # populate note data frame

    # first some utils we'll use in the loop below

    def pindex(sd):
        return (int(sd[0])*7 + int(sd[1]))

    def intclass(interval):
        interval = abs(interval)
        if interval == 0:
            return 'rep'
        elif interval == 1:
            return 'step'
        elif interval == 2:
            return 'slip'
        else:
            return 'leap'


    _data = defaultdict(list)
    for i_c, c in enumerate(corpus.chants):
        i = 1
        for i_w, w in enumerate(c.words):
            for i_s, s in enumerate(w.syllables):
                for i_n, n in enumerate(s.notes):

                    # identify note's location in the corpus

                    _data['chantID'].append(i_c)
                    _data['word'].append(i_w)
                    _data['syll'].append(i_s)
                    _data['note'].append(i_n)


                    # identify initial and final syllable (1) and word (2) boundaries

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
                    _data['boundary_before'].append(initial)
                    _data['boundary_after'].append(final)

                    # extract pitch and register features

                    _data['reg_abs'].append(n.letter[0])
                    _data['pc_abs'].append(n.letter[1])
                    _data['pitch_abs'].append( n.letter[0] + '.' + n.letter[1])
                    _data['reg_rel'].append(n.sd[0])
                    _data['pc_rel'].append(n.sd[1])
                    _data['pitch_rel'].append( n.sd[0] + '.' + n.sd[1])
                    

                    # calculate intervallic context


                    if i == 1:
                        _data['lint'].append(99)
                        _data['lint_class'].append('edge')
                        _data['lint_dir'].append('edge')
                    else:
                        interval = int(pindex(c.flatSD[i]) - pindex(c.flatSD[i-1]))
                        _data['lint'].append(interval)
                        _data['lint_class'].append(intclass(interval))
                        if interval > 0:
                            _data['lint_dir'].append('up')
                        elif interval < 0:
                            _data['lint_dir'].append('down')
                        else:
                            _data['lint_dir'].append('rep')

                    if i == len(c.flatSD)-2:
                        _data['rint_class'].append('edge')
                        _data['rint_dir'].append('edge')
                        _data['rint'].append(99)
                    else:
                        interval = int(pindex(c.flatSD[i+1]) - pindex(c.flatSD[i]))
                        _data['rint'].append(interval)
                        _data['rint_class'].append(intclass(interval))
                        if interval > 0:
                            _data['rint_dir'].append('up')
                        elif interval < 0:
                            _data['rint_dir'].append('down')
                        else:
                            _data['rint_dir'].append('rep')
                        

                    i += 1

    # add interval info



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
    
    c = cd.iloc[idx]

    htmlOut = ''
    htmlOut += f'<span style="font: 12px Roboto"><a href="http://corpus.music.yale.edu/displaychants?office={c.office}">{c.office}</a> | {fullGenre[c.genre]}'


    fullS = fullService[c.service]
    s = c.service
    htmlOut += f'<table><tr><td style="text-align:left;vertical-align:top">'

    htmlOut += f'<span style="font: 12px Roboto"><span style="font-weight:900;"><a href="http://corpus.music.yale.edu/displaychants?office={c.office}&service={s}">{fullS}</a>&nbsp;{c.ordinal} </span><br>'

    # htmlOut += f'<span style="font:18px Roboto; font-weight=900"><b>{fullS[0].upper()}</b><span style="font: 12px Roboto">{fullS[1:]}&nbsp;</span><br>'
    htmlOut += f'<span style="font:18px Roboto; font-weight=900"><b><a href="http://corpus.music.yale.edu/displaychants?genre={c.genre}&mode={c.modus}"><span title={fullGenre[c.genre]}>{c.genre}</span>&#8209;{c.modus}</b></span></a>'
    htmlOut += '</td><td style="text-align:left;vertical-align:top"><span style="font:32px volpiano;">'
    htmlOut += tenorclef(c.volpiano)
    htmlOut += '</span></td></tr></table><br>'
    for i in range(18): htmlOut += '&nbsp;'
    htmlOut += '<span style="font: 12px Merriweather;">{}</span><br><br><br>'.format(c.text.lower())
    display(HTML(htmlOut))
    return

def displayVolpiano(volpiano):
    htmlOut = ''
    htmlOut += '<span style="font:32px volpiano;">'
    htmlOut += tenorclef('1--'+volpiano)
    htmlOut += '</span>'
    display(HTML(htmlOut))
    return

# for _name in dir():
#     if _name.startswith('_'):
#         del globals()[_name]

def display_percent(x):    # used for easier-to-read probability tables
    if x == 0 or numpy.isnan(x):
        return ''
    else:
        return str(int(x*100)) + '%'


modesHapax = ['1e','4b','7a','7c']
modesRare = ['2g','2a','8c']
modesTransp = ['4a', '5c', '6c']
modesMain = ['1d','2d','3e','4e','5f','6f','7g','8g']
modesMore = modesMain + modesTransp
modesMost = modesMore + modesRare
modesAll  = modesMost + modesHapax

modesMainAuth = ['1d','3e','5f','7g']
modesMainPlag = ['2d','4e','6f','8g']
modesPsalm = ['1v','2v','3v','4v','5v','6v','7v','8v']

basicModes = modesMain 
psalmTones = modesPsalm

try:
    cd = pd.read_pickle('chant/chantData.zip')
    nd = pd.read_pickle('chant/noteData.zip')
except:
    cd = pd.read_pickle('chantData.zip')
    nd = pd.read_pickle('noteData.zip')

