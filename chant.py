from lmlo import lmloCorpus, tenorclef, fullService, fullGenre
import pandas as pd
import numpy
from collections import defaultdict, Counter
from IPython.core.display import display, HTML


n_limit = 8


gamut_pitches = ['0f','0g','1a','1b','1c','1d','1e','1f','1g','2a','2b','2c','2d','2e','2f','2g','3a','3b','3c','3d','3e']
gamut_volpiano = ['8','9','a','b','c','d','e','f','g','h','j','k','l','m','n','o','p','q','r','s','t']
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

def v2r(v):
  if v == '':
    return v

  numbers = list()
  for vchar in v:
    numbers.append(gamut_volpiano.index(vchar))
  min_n = min(numbers)
  output = '<'
  for i in range(len(numbers)):
    output += f'{numbers[i] - min_n:x}' 
  output += '>'

  return output

def v2c(v):
    output = ''
    if len(v) >= 2:
        for k in range(len(v)-1):
            v1 = gamut_volpiano.index(v[k])
            v2 = gamut_volpiano.index(v[k+1])
            if v1 == v2:
                output += '='
            elif v2 < v1:
                output += '-'
            else:
                output += '+'

    return output

def _recalculate():

    from cltk.stem.latin.syllabifier import Syllabifier
    syllabifier = Syllabifier()

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

    chants = pd.DataFrame(_data)
    chants.to_pickle('chantData.zip')

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



    notes = pd.DataFrame(_data)
    notes.to_pickle('noteData.zip')
    
    chantsnotes = chants.merge(notes)
    syllables = defaultdict(list)
    override = dict()
    override['eius'] = ['e','ius']
    override['dei'] = ['de','i']
    override['deus'] = ['de','us']
    override['quia'] = ['qui','a']
    override['christi'] = ['chris','ti']
    override['christe'] = ['chris','te']
    override['eum'] = ['e','um']
    override['deum'] = ['de','um']
    override['meum'] = ['me','um']
    override['meus'] = ['me','us']
    override['christo'] = ['chris','to']
    override['christus'] = ['chris','tus']
    override['christum'] = ['chris','tum']
    override['mei'] = ['me','i']
    override['ei'] = ['e','i']
    override['cui'] = ['cu','i']
    override['israel'] = ['is','ra','el']
    override['sanguine'] = ['san','gui','ne']
    override['meis'] = ['me','is']
    override['eis'] = ['e','is']
    override['fidei'] = ['fi','de','i']
    override['sanguinem'] = ['san','gui','nem']
    override['lingua'] = ['lin','gua']
    override['thronum'] = ['thro','num']
    override['pulchra'] = ['pul','chra']
    override['oleum'] = ['o','le','um']
    override['adiutor'] = ['ad','iu','tor']
    override['sanguis'] = ['san','guis']
    override['sanguinis'] = ['san','gui','nis']
    override['huic'] = ['hu','ic']
    override['alleluia'] = ['al','le','lu','ia']
    override['michael'] = ['mi','cha','el']
    override['noe'] = ['no','e']
    
    
    for i, c in chants.iterrows():
      if c.modus not in basicModes+['6c']:
          continue
      # if i>200: break
      words = c.text.lower().split()
      vwords = c.volpiano[4:-3].split('--')
      if len(words) != len(vwords):
        # print(f'oops: {len(words)} {len(vwords)}')
        # print(words)
        # print(vwords)    
        vwords[-2] = vwords[-2] + '-' + vwords[-1]
        vwords.pop(-1)
        # print('--fixing--')
        # print(words)
        # print(vwords)
      for j in range(len(words)):
        if words[j] in override:
          sylls = override[words[j]]
        else:
          sylls = syllabifier.syllabify(words[j].lower())
        vsylls = vwords[j].split('-')
        if len(sylls) != len(vsylls):
          sylls = [f'[{words[j]}]'] * len(vsylls)
        for k in range(len(vsylls)):
          syllables['chantID'].append(c.chantID)
          syllables['syllable'].append(sylls[k])
          syllables['last_syll'].append(k+1 == len(vsylls))
          v = vsylls[k]
          syllables['n_notes'].append(len(v))
          syllables['volpiano'].append(v)
          notes = ''
          for vchar in v:
            notes += f'{gamut_pitches[gamut_volpiano.index(vchar)]} '
          syllables['notes'].append(notes)
          syllables['pitch_initial'].append(gamut_pitches[gamut_volpiano.index(v[0])])
          syllables['pitch_final'].append(gamut_pitches[gamut_volpiano.index(v[-1])])
          syllables['t_type'].append(v2r(v))
          syllables['e_type'].append(v2r(v[0]+v[-1]))
          syllables['c_type'].append(v2c(v))
   

    syllables = pd.DataFrame(syllables)
    modekey = chantsnotes.query("word == 0 and syll == 0 and note == 0").set_index('chantID').modus.to_frame()
    syllables = syllables.join(modekey.modus, on='chantID', how='inner')
    syllables['extrema'] = syllables['pitch_initial'] + '-' + syllables['pitch_final']
    syllables.to_pickle('syllableData.zip')


    ngrams = defaultdict(list)
    
    
    for i, c in chants.iterrows():
        # if i>0: break
        v = c.volpiano.replace('-','')
    
        # V = v with duplicate pitches removed
    
        V = v[0]
        for k in range(1, len(v)):
            if v[k] != V[-1]:
                V += v[k]
    
        
        for n in range(1, n_limit+1):
            for k in range(1,len(V)-n):
                v = V[k:k+n]
                ngrams['chantID'].append(c.chantID)
                ngrams['pos'].append(k)
                ngrams['n_notes'].append(len(v))
                ngrams['volpiano'].append(v)
                notes = ''
                for vchar in v:
                    notes += f'{gamut_pitches[gamut_volpiano.index(vchar)]} '
                ngrams['notes'].append(notes)
                ngrams['pitch_initial'].append(gamut_pitches[gamut_volpiano.index(v[0])])            
                ngrams['pitch_final'].append(gamut_pitches[gamut_volpiano.index(v[-1])])
                ngrams['t_type'].append(v2r(v))
                ngrams['e_type'].append(v2r(v[0]+v[-1]))
                ngrams['c_type'].append(v2c(v))
    
    ngrams = pd.DataFrame(ngrams)
    ngrams = ngrams.join(modekey.modus, on='chantID', how='inner')
    
    ngrams['extrema'] = ngrams['pitch_initial'] + '-' + ngrams['pitch_final']
    
    print('making pickles')
    ngrams.to_pickle('ngramData.zip')


def vdisplay(volpiano, size=24, addClef = False, color='black', tenorClef=True):
    if addClef:
        volpiano = '1-'+volpiano
    if tenorClef:
        volpiano = tenorclef(volpiano)

    output = f'<span style="font:{size}px volpiano;color:{color}">{volpiano}</span>'
    display(HTML(output))
    return 

def displayChant(idx):
    
    c = chants.iloc[idx]

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



try:
    chants = pd.read_pickle('chant/chantData.zip')
    notes = pd.read_pickle('chant/noteData.zip')
    syllables = pd.read_pickle('chant/syllableData.zip')
    ngrams = pd.read_pickle('chant/ngramData.zip')

except:
    chants = pd.read_pickle('chantData.zip')
    notes = pd.read_pickle('noteData.zip')
    syllables = pd.read_pickle('syllableData.zip')
    ngrams = pd.read_pickle('ngramData.zip')

