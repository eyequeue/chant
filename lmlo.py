# provides lmlo module

# CANONICAL VERSION AS OF AUGUST 2017
# NOW LIVES IN webapp/chantomics
# ASSUMES PYTHON 3

# pickling of data is currently disabled; it doesn't save enough time to warrant the trouble

import re       # module for pattern matching with Regular Expressions
import string
import os.path
import sys
import time
import math
import collections
import random
import gc
import os

_VERBOSE = False

# corpus provided at end of module doesn't contain chants with missing notes


# from http://stackoverflow.com/questions/3012421/python-lazy-property-decorator
# used for lazy evaluation of flatLetter and flatSD

class lazy_property(object):
    '''
    meant to be used for lazy evaluation of an object attribute.
    property should represent non-mutable data, as it replaces itself.
    '''

    def __init__(self,fget):
        self.fget = fget
        self.__name__ = fget.__name__


    def __get__(self,obj,cls):
        if obj is None:
            return None
        value = self.fget(obj)
        setattr(obj,self.__name__,value)
        return value



def ngrams( inputList, n ):
    return list(zip(*[inputList[i:] for i in range(n)]))

################################################################################################
# utilities for translating between LMLO scaledegrees, numeric scale degrees, and letter names #
################################################################################################

# basic gamuts

lmloGamut = '%*-0123456789>' # definitely don't change this!
sdGamut = '1234567' # probably don't change
letterGamut = 'abcdefg' # probably don't change
octaveGamut = '0123' # can be changed/customized
basicModes = ['1d','2d','3e','4e','5f','6f','7g','8g']
expBasicModes = ['1d','2d','3e','4e','5f','6f','6c','7g','8g']

gamut = [
    '0d',
    '0e',
    '0f',
    '0g',
    '1a',
    '1b',
    '1c',
    '1d',
    '1e',
    '1f',
    '1g',
    '2a',
    '2b',
    '2c',
    '2d',
    '2e',
    '2f',
    '2g',
    '3a',
    '3b',
    '3c',
    '3d'

]
gamut_t = dict()
gamut_t[0] = gamut
gamut_t[1] = [
    '0e',
    '0f',
    '0g',
    '1a',
    '1b',
    '1c',
    '1d',
    '1e',
    '1f',
    '1g',
    '2a',
    '2b',
    '2c',
    '2d',
    '2e',
    '2f',
    '2g',
    '3a',
    '3b',
    '3c'
]
gamut_t[-1] = [
    '0c',
    '0d',
    '0e',
    '0f',
    '0g',
    '1a',
    '1b',
    '1c',
    '1d',
    '1e',
    '1f',
    '1g',
    '2a',
    '2b',
    '2c',
    '2d',
    '2e',
    '2f',
    '2g',
    '3a'
]
gamut_t[3] = [
    '0f',
    '0g',
    '1a',
    '1b',
    '1c',
    '1d',
    '1e',
    '1f',
    '1g',
    '2a',
    '2b',
    '2c',
    '2d',
    '2e',
    '2f',
    '2g',
    '3a',
    '3b',
    '3c',
    '3d'
]
gamut_t[-2] = [
    '0a',
    '0b',
    '0c',
    '0d',
    '0e',
    '0f',
    '0g',
    '1a',
    '1b',
    '1c',
    '1d',
    '1e',
    '1f',
    '1g',
    '2a',
    '2b',
    '2c',
    '2d',
    '2e',
    '2f'
]
gamut_t[4] = [
    '0g',
    '1a',
    '1b',
    '1c',
    '1d',
    '1e',
    '1f',
    '1g',
    '2a',
    '2b',
    '2c',
    '2d',
    '2e',
    '2f',
    '2g',
    '3a',
    '3b',
    '3c',
    '3d',
    '3e'
]
gamut_t[-3] = [
    'GG',
    '0a',
    '0b',
    '0c',
    '0d',
    '0e',
    '0f',
    '0g',
    '1a',
    '1b',
    '1c',
    '1d',
    '1e',
    '1f',
    '1g',
    '2a',
    '2b',
    '2c',
    '2d',
    '2e'
]

startToken = '>S'
endToken = '>E'

def sortMagic(theTuple):
    t = theTuple[0]
    for i in range(len(octaveGamut)):
        t = t.replace(octaveGamut[i],str(i))
    return t

def sortMagicString(t):
    for i in range(len(octaveGamut)):
        t = t.replace(octaveGamut[i],str(i))
    return t

# turns an LMLO scaledegree character into a two-char octave+sd code

def lmlo2sd (lmloChar):
    i = lmloGamut.find(lmloChar)
    if i == -1:
        raise NameError("Can't translate lmloChar: "+lmloChar)
    sd = sdGamut[(i-4) % 7]
    octave = octaveGamut[(i+3)//7]
    return octave+sd

# turns a two-char octave+sd code into a two-char octave+letter name given a final
# (assumes that scale degree '=1' is in the '=' octave of letter names)

def sd2letter (sd, mode):
    final = mode[1].lower()
    if final in ['v', 't']:
        number = int(mode[0])
        if number in [1, 2]:
            final = 'd'
        elif number in [3, 4]:
            final = 'e'
        elif number in [5, 6]:
            final = 'f'
        elif number in [7, 8]:
            final = 'g'
        else:
            raise NameError("Can't translate mode number: " + number)
    if final not in letterGamut:
        raise NameError("Can't translate final: " + final)
    if len(sd) != 2 and sd[0] not in octaveGamut and sd[1] not in sdGamut:
        raise NameError("Can't translate sd: " + sd)
    i = octaveGamut.find(sd[0]) * 7 + \
        sdGamut.find(sd[1]) + \
        letterGamut.find(final)
    if mode.lower in ['2a', '4a', '6c', '5c']: i += 7 
    letter = letterGamut[i%7]
    octave = octaveGamut[i//7]
    return octave+letter

# def letter2sd (letter, mode):


# NEED TO WRITE letter2sd !!!!!
vchar2tc = dict()
vchar2tc['D'] = 'E'
vchar2tc['E'] = '8'
vchar2tc['8'] = '9'
vchar2tc['9'] = 'a'
vchar2tc['a'] = 'b'
vchar2tc['b'] = 'c'
vchar2tc['c'] = 'd'
vchar2tc['d'] = 'e'
vchar2tc['e'] = 'f'
vchar2tc['f'] = 'g'
vchar2tc['g'] = 'h'
vchar2tc['h'] = 'j'
vchar2tc['j'] = 'k'
vchar2tc['k'] = 'l'
vchar2tc['l'] = 'm'
vchar2tc['m'] = 'n'
vchar2tc['n'] = 'o'
vchar2tc['o'] = 'p'
vchar2tc['p'] = 'q'
vchar2tc['q'] = 'r'
vchar2tc['r'] = 's'
vchar2tc['s'] = '7'
vchar2tc['t'] = '7'
vchar2tc['5'] = '6'
vchar2tc['1'] = '6'
vchar2tc['-'] = '-'

def tenorclef(volpiano):

    output = ''
    for v in volpiano:
        output += vchar2tc[v]
    return output




def letter2number (letter):
    try:
        return letterGamut.index(letter[1]) + 7 * octaveGamut.index(letter[0])
    except:
        print("letter2number: cant translate", letter)
        return 99
    
l2v = dict()
l2v[octaveGamut[0]+'c'] = 'C'
l2v[octaveGamut[0]+'d'] = 'D'
l2v[octaveGamut[0]+'e'] = 'E'
l2v[octaveGamut[0]+'f'] = '8'
l2v[octaveGamut[0]+'g'] = '9'
l2v[octaveGamut[1]+'a'] = 'a'
l2v[octaveGamut[1]+'b'] = 'b'
l2v[octaveGamut[1]+'c'] = 'c'
l2v[octaveGamut[1]+'d'] = 'd'
l2v[octaveGamut[1]+'e'] = 'e'
l2v[octaveGamut[1]+'f'] = 'f'
l2v[octaveGamut[1]+'g'] = 'g'
l2v[octaveGamut[2]+'a'] = 'h'
l2v[octaveGamut[2]+'b'] = 'j'
l2v[octaveGamut[2]+'c'] = 'k'
l2v[octaveGamut[2]+'d'] = 'l'
l2v[octaveGamut[2]+'e'] = 'm'
l2v[octaveGamut[2]+'f'] = 'n'
l2v[octaveGamut[2]+'g'] = 'o'
l2v[octaveGamut[3]+'a'] = 'p'
l2v[octaveGamut[3]+'b'] = 'q'
l2v[octaveGamut[3]+'c'] = 'r'
l2v[octaveGamut[3]+'d'] = 's'
l2v[octaveGamut[3]+'d'] = 't'
l2v[endToken] = '5'
l2v[startToken] = '1'


l2vsmall = dict()
l2vsmall[octaveGamut[0]+'d'] = 'D'
l2vsmall[octaveGamut[0]+'e'] = 'E'
l2vsmall[octaveGamut[0]+'f'] = '('
l2vsmall[octaveGamut[0]+'g'] = ')'
l2vsmall[octaveGamut[1]+'a'] = 'A'
l2vsmall[octaveGamut[1]+'b'] = 'B'
l2vsmall[octaveGamut[1]+'c'] = 'C'
l2vsmall[octaveGamut[1]+'d'] = 'D'
l2vsmall[octaveGamut[1]+'e'] = 'E'
l2vsmall[octaveGamut[1]+'f'] = 'F'
l2vsmall[octaveGamut[1]+'g'] = 'G'
l2vsmall[octaveGamut[2]+'a'] = 'H'
l2vsmall[octaveGamut[2]+'b'] = 'J'
l2vsmall[octaveGamut[2]+'c'] = 'K'
l2vsmall[octaveGamut[2]+'d'] = 'L'
l2vsmall[octaveGamut[2]+'e'] = 'M'
l2vsmall[octaveGamut[2]+'f'] = 'N'
l2vsmall[octaveGamut[2]+'g'] = 'O'
l2vsmall[octaveGamut[3]+'a'] = 'P'
l2vsmall[octaveGamut[3]+'b'] = 'Q'
l2vsmall[octaveGamut[3]+'c'] = 'R'
l2vsmall[octaveGamut[3]+'d'] = 'S'
l2vsmall[endToken] = '5'
l2vsmall[startToken] = '1'

vchar2l = dict()
vchar2l['D'] = octaveGamut[0]+'d'
vchar2l['E'] = octaveGamut[0]+'e'
vchar2l['8'] = octaveGamut[0]+'f'
vchar2l['9'] = octaveGamut[0]+'g'
vchar2l['a'] = octaveGamut[1]+'a'
vchar2l['b'] = octaveGamut[1]+'b'
vchar2l['c'] = octaveGamut[1]+'c'
vchar2l['d'] = octaveGamut[1]+'d'
vchar2l['e'] = octaveGamut[1]+'e'
vchar2l['f'] = octaveGamut[1]+'f'
vchar2l['g'] = octaveGamut[1]+'g'
vchar2l['h'] = octaveGamut[2]+'a'
vchar2l['j'] = octaveGamut[2]+'b'
vchar2l['k'] = octaveGamut[2]+'c'
vchar2l['l'] = octaveGamut[2]+'d'
vchar2l['m'] = octaveGamut[2]+'e'
vchar2l['n'] = octaveGamut[2]+'f'
vchar2l['o'] = octaveGamut[2]+'g'
vchar2l['p'] = octaveGamut[3]+'a'
vchar2l['q'] = octaveGamut[3]+'b'
vchar2l['r'] = octaveGamut[3]+'c'
vchar2l['s'] = octaveGamut[3]+'d'
vchar2l['t'] = octaveGamut[3]+'e'
vchar2l['5'] = endToken
vchar2l['1'] = startToken

def v2ngram( vstring ):
    noteList = list()
    for c in vstring:
        noteList.append(vchar2l[c])
    return tuple(noteList)

def ngram2v( ngram ):
    noteList = ''
    for c in ngram:
        noteList += l2v[c]
    return noteList


v2small = dict()
v2small['-'] = '-'
v2small['D'] = 'Q'
v2small['E'] = 'R'
v2small['8'] = '('
v2small['9'] = ')'
v2small['a'] = 'A'
v2small['b'] = 'B'
v2small['c'] = 'C'
v2small['d'] = 'D'
v2small['e'] = 'E'
v2small['f'] = 'F'
v2small['g'] = 'G'
v2small['h'] = 'H'
v2small['j'] = 'J'
v2small['k'] = 'K'
v2small['l'] = 'L'
v2small['m'] = 'M'
v2small['n'] = 'N'
v2small['o'] = 'O'
v2small['p'] = 'P'
v2small['q'] = 'Q'
v2small['r'] = 'R'
v2small['s'] = 'S'
   
fullGenre = dict()
fullGenre['$'] = 'suffrage' # (usually an antiphon)
fullGenre['A'] = 'psalm antiphon' # (Agnus at Mass)
fullGenre['D'] = 'dialogue (Vx + Rx)'
fullGenre['E'] = 'canticle antiphon'
fullGenre['H'] = 'hymn'
fullGenre['I'] = 'invitatory'
fullGenre['J'] = 'alleluia at Mass'
fullGenre['K'] = 'canticle text' # (Kyrie at Mass)
fullGenre['Q'] = 'sequence'
fullGenre['R'] = 'responsory Rx' # (gradual at Mass)
fullGenre['U'] = 'alleluia verse'
fullGenre['V'] = 'responsory Vx' # (gradual at Mass)
fullGenre['W'] = 'misc. verse' # (not responsory or alleluia)
fullGenre['X'] = 'doxology'
fullGenre['Z'] = 'Benedicamus Domino'
fullGenre['a'] = 'antiphon [incipit]'
fullGenre['i'] = 'invitatory [incipit]'
fullGenre['l'] = 'lesson [incipit]'
fullGenre['r'] = 'responsory Rx [incipit]'
fullGenre['v'] = 'responsory Vx [incipit]'
# the next two are added as catchall categories, not original to Hughes
fullGenre['O'] = 'other'
fullGenre['T'] = 'incipit'

fullGenreShort = dict()
fullGenreShort['A'] = 'antiphon A'
fullGenreShort['E'] = 'antiphon E'
fullGenreShort['I'] = 'invitatory'
fullGenreShort['R'] = 'responsory R'
fullGenreShort['V'] = 'responsory V'
fullGenreShort['O'] = 'other'
fullGenreShort['T'] = 'incipit'

fullService = dict()
fullService['$'] = 'suffrage'
fullService['C'] = 'Compline'
fullService['H'] = 'LittleHrs'
fullService['L'] = 'Lauds'
fullService['M'] = 'Matins'
fullService['N'] = 'Nones'
fullService['P'] = 'Prime'
fullService['Q'] = 'unknown'
fullService['R'] = 'Procession'
fullService['S'] = 'Sext'
fullService['T'] = 'Terce'
fullService['U'] = 'other'
fullService['V'] = 'Vespers&nbsp;1'
fullService['W'] = 'Vespers&nbsp;2'

genreOrder = [
    'I', # 'invitatory'
    'A', # 'antiphon or Agnus'
    'E', # 'antiphon for gospel (or monastic) canticles'
    'R', # 'responsory or gradual'
    'V', # 'verse of responsory or gradual'
    '$', # 'suffrage (usually an antiphon)'
    'D', # 'dialogue (versicle and response)'
    'H', # 'hymn'
    'J', # 'alleluia at Mass'
    'K', # 'canticle text or Kyrie'
    'Q', # 'sequence'
    'U', # 'alleluia verse'
    'W', # 'verse (not responsory or alleluia)'
    'X', # 'doxology'
    'Z', # 'Benedicamus Domino'
    'a', # 'antiphon or Agnus [incipit]'
    'i', # 'invitatory [incipit]'
    'l', # 'lesson [incipit]'
    'r', # 'responsory or gradual [incipit]'
    'v', # 'verse of responsory or gradual [incipit]'
]
GenreOrder = [
    'I', # 'invitatory'
    'A', # 'antiphon or Agnus'
    'E', # 'antiphon for gospel (or monastic) canticles'
    'R', # 'responsory or gradual'
    'V', # 'verse of responsory or gradual'
    'O', # other
    'T', # incipits
]
serviceOrder = [
    'V',  # 'First Vespers'
    'C',  # 'Compline'
    'M',  # 'Matins'
    'L',  # 'Lauds'
    'W',  # 'Second Vespers'
    'P',  # 'Prime'
    'T',  # 'Terce'
    'S',  # 'Sext'
    'N',  # 'Nones'
    'H',  # 'Little hours'
    'Q',  # 'Unknown or unidentified service'
    'R',  # 'Procession'
    '$',  # 'Memorial service or suffrage'
    'U'   # 'other'
]
ServiceOrder = [
    'V',  # 'First Vespers'
    'M',  # 'Matins'
    'L',  # 'Lauds'
    'W',  # 'Second Vespers'
    'H',  # 'Little hours'
    'U'   # 'other'
]

#####################################################################################
# hierarchy of classes: lmloCorpus > lmloChant > lmloWord > lmloSyllable > lmloNote #
#####################################################################################

class lmloNote:
    def __init__(self, sd, letter):
        self.sd = sd
        self.letter = letter

class lmloSyllable:
    def __init__(self):
        self.notes = list() # list of lmloNote instances

class lmloWord:
    def __init__(self, text = ''):
        self.text = text
        self.syllables = list() # list of lmloSyllable instances

class lmloChant:
    def __init__(self, mode):
        if len(mode) != 2 or mode[0] not in '12345678' or mode[1] not in 'abcdefgABCDEFGvtVT':
            raise NameError("Unparseable mode: " + mode)
        if mode[0] not in '12345678':
            raise NameError("Unknown mode number: " + mode[0])
        self.mode = mode
        self.words = list()
        self.ignoreMode = False
        self.ignoreDupe = False
        self.ignoreMissingNotes = False # indicates whether illegible notes are marked as '?' in the encoding
        self.pmode = ''
        self.tfinal = ''
        
    @lazy_property
    def volpiano(self):
        volpiano = '1---'
        for w in self.words:
            for s in w.syllables:
                for n in s.notes:
                    volpiano += l2v[n.letter]
                volpiano += '-'
            volpiano += '-'
        volpiano += '5'
        return volpiano


    @lazy_property
    def flatSD(self):
        flat = [startToken]
        for w in self.words:
            for s in w.syllables:
                for n in s.notes:
                    flat.append(n.sd)
        flat.append(endToken)
        return flat
        

    @lazy_property
    def flatLetter(self):
        flat = [startToken]
        for w in self.words:
            for s in w.syllables:
                for n in s.notes:
                    flat.append(n.letter)
        flat.append(endToken)
        return flat
        
        
        
    def ignore(self):
        return self.ignoreMode or self.ignoreDupe or self.ignoreMissingNotes
        
    @lazy_property
    def fulltext(self):
        ws = ''
        for w in self.words:
            ws += w.text + ' '
        return ws[0:-1]


    @lazy_property
    def syllableBoundaries(self):
    
        ###########################################################################
        # WARNING: syllableBoundaries not safe for use with stripDuplicatePitches #
        ###########################################################################
    
        output = [2]  # start symbol is a word boundary
        for w in self.words:
            for s in w.syllables:
                for n in s.notes:
                    output.append(0)
                output[-1] += 1
            output[-1] += 1
        output.append(0) # end symbol is not a syllable boundary
        
        return output
 
 
 
class lmloCorpus:
    def __init__(self, samplePercentage = 100):

        lmloFilename = f'{os.path.dirname(__file__)}/data/v2-CHNT.txt'
        
        #######################################################
        # first pass through the LMLO data:                   #
        # * find all header lines and the chant lines we want #
        # * extract metadata from headers                     #
        # * clean up chant lines a bit                        #
        # * populate the self.chants data structure            #
        #######################################################

        f = open(lmloFilename, "r", encoding='latin-1')

        lmloDataLines = list()
        for line in f:
            lmloDataLines.append(line.rstrip())   # strip off trailing newline/CR

        self.chants = list()
        theHeader = ""
        theMode = ""

        for i in range(len(lmloDataLines)):
        
            # look for new office header
            # there are a few places where one of these seems to be missing;
            # see commented-out code that follows, which seems to catch exceptions.
            # for the moment, we'll live with the fact that a few "offices" are collapsed
        
            matchPageHeader = re.search('®TP0¯.*?\[(.*)\]', lmloDataLines[i])
            if matchPageHeader:
                theOffice = matchPageHeader.group(1)
                if theOffice[0:5] == 'Begin':
                    matchFile = re.search('.*CH-(.*)', theOffice) 
                    if matchFile.group(1) == 'D-0':
                        theFile = "[Humbert] "
                    elif matchFile.group(1)[0:3] == 'D-8':
                        theFile = "[Humbert Sanct.] "
                    elif matchFile.group(1) == 'D-9':
                        theFile = "[Humbert] "
                    elif matchFile.group(1)[0:2] == 'D-':
                        theFile = "[Humbert Temp.] "
                    elif matchFile.group(1)[0:2] in ['X','Y']:
                        theFile = "[Feast] "
                    else:
                        theFile = '[Saint] '
 
                # truncate office names like "X JU72 IUSTUS of Beauvais"
                if theOffice[0:2] == 'X ':
                    theOffice = theOffice[7:]

                theOffice = theFile + theOffice

 



            matchHeaderLine = re.search('\\|g(.*?) \\=(.*?)\\.(..)',lmloDataLines[i]) # parens in the regex aren't part of the 
                                                                        # pattern to be matched but indicate parts
                                                                        # of the pattern we'll want to refer to later

            # if it's a chant header extract the metadata

            if matchHeaderLine:                         
                theHeader = matchHeaderLine.group(0)      # group(0) = the whole regex (matched pattern)
                theMode = matchHeaderLine.group(3)        # group(3) = the third paren group in the regex
                theService = matchHeaderLine.group(2)[0]  # = first character of the second paren group in the regex
                theGenre = matchHeaderLine.group(2)[1]    # = second character of the second paren group in the regex
                theNumber = matchHeaderLine.group(2)[2:]
                theIndex = matchHeaderLine.group(1)[:-1]
#                     print('    ', theHeader, 'index:', theIndex, 'number:', theNumber)
                continue                             # and now we can skip to the next line; we got what we wanted

            # line with '\ ' is [usually] a line of chant
            # this is [usually] the second of Hughes's four representations of each chant
            # so we've got all the words and syllables and stuff

            # skip lines that don't start with '\ '
            matchChantLine = re.search('^\\\\ ',lmloDataLines[i])
            if not matchChantLine: 
#                     print("              ", i, "doesn't start with '\ '")
                continue

            # skip lines containing ellipses (i.e. lines 11000 and 14127)
            matchEllipsis = re.search('\\.\\.\\.',lmloDataLines[i])
            if matchEllipsis: 
#                     print('              ', i, 'uh oh, an ellipsis')
                continue  
        
            # some chant index lines are broken up over two lines in the file, so
            # if the line doesn't contain '\()' [optionally with stuff inside the parens] 
            # then it's continued on the next line according to LMLO conventions

            while not re.search('\\\\\\(.*?\\)',lmloDataLines[i]):  # while makes this iterative; we keep gluing lines
                                                           # together until we match '\()' or '\(*stuff*)'
               lmloDataLines[i] = lmloDataLines[i] + lmloDataLines.pop(i+1)    # glue this line together with the next one, which is deleted;
               lmloDataLines.append("")                      # add a blank line at the end so the length of lmloDataLines doesn't change;
                                                    # if we don't add blanks the big loop we're in will freak out since i
                                                    # was set to iterate over the original length of lmloDataLines;
                                                    # those empty lines will be ignored b/c they aren't headers or chantlines
#                    print('              ', i, 'gluing some lines together')
    
            # get rid of footnotes, which by LMLO convention have the form '(!*stuff*)'

            re.sub("\\(!.*?\\)","",lmloDataLines[i]) # what this really does is replace a footnote with an empty string

            # populate self.chants, a list of dicts that hold data and metadata for each chant

            if random.random() > samplePercentage / 100:
                continue

            try:
                thisChant = lmloChant(theMode)
            except:
#                     print('              ', i, 'theMode: ', theMode, 'FAILED')
                continue
            if theMode[0] in '1357':
                thisChant.ambitus = 'authentic'
            elif theMode[0] in '2468':
                thisChant.ambitus = 'plagal'
            if theMode[0] in '12':
                thisChant.maneria = 'protus'
            elif theMode[0] in '34':
                thisChant.maneria = 'deuterus'
            elif theMode[0] in '56':
                thisChant.maneria = 'tritus'
            elif theMode[0] in '78':
                thisChant.maneria = 'tetrardus'
        
            thisChant.office = theOffice
            thisChant.service = theService
            thisChant.genre = theGenre
            thisChant.number = theNumber
            thisChant.index = theIndex
            thisChant.header = theHeader
            thisChant.lmloEncoding = lmloDataLines[i]


            # add simplified Service and Genre attributes (with init caps)

            thisChant.Service = thisChant.service
            if thisChant.Service in ['C', 'P', 'T', 'S', 'N']:
                thisChant.Service = 'H' # collapse Compline (!) and the four Little Hours into "little hours"
            if thisChant.Service in ['R', '$', 'Q']:
                thisChant.Service = 'U' # collapse misc infrequent services and unknowns into "other"

            thisChant.Genre = thisChant.genre
            if thisChant.Genre in ['$', 'D', 'H', 'J', 'K', 'Q', 'U', 'W', 'X', 'Z']:
                thisChant.Genre = 'O' # collapse "misc" chants into one genre
            if thisChant.Genre in ['a', 'i', 'l' ,'r', 'v']:
                thisChant.Genre = 'T' # collapse incipits into one genre


            self.chants.append(thisChant)
#                 print('              ', i, 'theMode: ', theMode, 'success!')

        ####################################################################
        # second pass: process each chant into words, notes, and syllables #
        ####################################################################


        for i, theChant in enumerate(self.chants):


            bStatus = '?'

            verboseParse = False
            if theChant.index in [11000, 14127]:
                verboseParse = True
    
            chantWords = theChant.lmloEncoding.split()[1:-1]     # each chantWord has the form illustret.14.43454.21

            if verboseParse: print('\nLINE',theChant.index)

            for theCWtext in chantWords:
        
                if verboseParse: print('parsing',theCWtext)

                prevSD = ''
                syllables = theCWtext.split('.')   # split the chantword on periods (which separate syllables in the encoding)
                if len(syllables) == 1: 
                    if verboseParse:
                        print ('...skipping')
                    if theCWtext.find('<') != -1:
                        bStatus = 'b'
                        if verboseParse:
                            print ('[B-mollis]')
                    if theCWtext.find(chr(21)) != -1:
                        bStatus = 'h'
                        if verboseParse:
                            print ('[B-durus]')
                    continue
                theWord = lmloWord(syllables[0])   # everything before the first . in a chantword is the text word
            
                # now look at subsequent parts of the chantword, which are notes by syllable
            
                for j in range(len(syllables)-1):
                    
                    if verboseParse:
                        print(f'  [{theChant.mode}:{bStatus}] syllable: {syllables[j+1]}')
            
                    theSyllData = syllables[j+1]    
                    if len(theSyllData) == 0: 
                        
                        if verboseParse:
                            print('  ...skipping')
                        continue

                    theSyllable = lmloSyllable()
                
                    for c in range(len(theSyllData)):   # and now we go character by character through the syllable
                        if theSyllData[c] == '<':
                            bStatus = 'b'
                            if verboseParse:
                                print ('[B-mollis]')
                        if theSyllData[c] == chr(21):
                            bStatus = 'h'
                            if verboseParse:
                                print ('[B-durus]')
                        if theSyllData[c] == '=' and prevSD != '':
                            sd = prevSD       # if we see a '=' we repeat the previous pitch
                        else:
                            try:
                                sd = lmlo2sd(theSyllData[c])  # this throws an error if we see anything but a pitch character
                            except:
                                #print 'possible typo in LMLO data: ' +theSyllData[c]#+' in '+ theSyllData + ' in ' + theChant.lmloMetadata['lmlo-encoding']

                                # flag chants having '?' for pitch (indicates illegible/damaged MS)
                                if theSyllData[c] == '?':
                                    theChant.ignoreMissingNotes = True


                                continue   # in which case we simply ignore and skip to the next character
                        # if we're still here then sd (the current character) is a scale degree
                        theNote = lmloNote(sd, sd2letter(sd, theChant.mode)) 
                        theSyllable.notes.append(theNote) 
                        
                        if len(theSyllable.notes) == 0: print('ZERO NOTE SYLLABLE')
                    
                    theWord.syllables.append(theSyllable)
                theChant.words.append(theWord)
                
            # prune out any zero-syllable words that slipped by
                
            i = 0
            while i+1 < len(theChant.words):
                if len(theChant.words[i].syllables) == 0:
                    print(theChant.words[i].text)
                    theChant.words.pop(i)
                else:
                    i += 1

            # add start tokens where appropriate
            
            firstSyllable = lmloSyllable()
            firstSyllable.notes.append(startToken)
            firstWord = lmloWord(startToken)
            firstWord.syllables.append(firstSyllable)
            
            lastSyllable = lmloSyllable()
            lastSyllable.notes.append(endToken)
            lastWord = lmloWord(endToken)
            lastWord.syllables.append(lastSyllable)
                
        # 10/16/2016: why are we doing this? investigate and fix!

        for i,c in enumerate(self.chants):
            if c.ignoreMissingNotes:
                self.chants.pop(i)
                i -= 1

        for i,c in enumerate(self.chants):
            c.ID = i



    def ignoreDuplicateChants( self, verbose = False ):
        ignored = 0
        for i, c1 in enumerate(self.chants):
            for c2 in self.chants[i+1:]:
                if c1.flatLetter == c2.flatLetter:
#                     print "[{}] {}: {}".format(c1.office, fullService[c1.service], fullGenre[c2.genre])
#                     print c1.fulltext
#                     print "[{}] {}: {}".format(c2.office, fullService[c2.service], fullGenre[c2.genre])
#                     print c2.fulltext
#                     print

                    ignored += 1
                    c2.ignoreDupe = True
        return ignored
    
#     def addFilter(self, fType, fValue)
#     
#         fTypes = ['mode','genre','service']
#         
#         if fType not in fTypes:
#             return False
#         
#         if 
        
    def selectMode(self, modes):
    
        self.ignored = 0
        self.retained = 0
        self.modeFilter = set()

        def filter(attr):
            for c in self.chants:
                if modes != ['all'] and getattr(c, attr) not in modes:
                    c.ignoreMode = True
                    self.ignored += 1
                else:
                    self.modeFilter.add(c.mode)
                    c.ignoreMode = False
                    if not c.ignoreDupe:     # modify this line if other ignore types are added
                        self.retained += 1
    
        if isinstance(modes, str):
            modes = [modes]
        if modes in [['protus'],['deuterus'],['tritus'],['tetrardus']]:
            list(filter('maneria'))
        elif modes in [['authentic'],['plagal']]:
            list(filter('ambitus'))
        else:
            list(filter('mode'))
#        print 'filter = {}, {} chants ({} ignored)'.format(modes, self.retained, self.ignored)

    def selected( self ):
    
        l = list()
        for c in self.chants:
            if not c.ignoreMode and not c.ignoreDupe:
                l.append(c)
        return l
        
    def randomizeTrainingAndTest( self, testProportion ):
        
        n = len(self.chants)
        shuffled = random.sample( list(range(n)), n )
        cutoff = int(testProportion * n)
        self.testIndexes = shuffled[0:cutoff]
        self.trainingIndexes = shuffled[cutoff:]


    # if randomTrainingAndTest() isn't run before calling trainingIndexes, default to 20% test set
        
    @lazy_property
    def trainingIndexes (self):
        self.randomizeTrainingAndTest(.2)
        return self.trainingIndexes
    
    def stripDuplicatePitches( self ):
    
    # IS IT NECESSARY TO REMOVE PITCHES FROM WORD-BY-WORD REPRESENTATION?
    
        for c in self.chants:
            i = 0
            while i < len(c.flatLetter)-1:
                while c.flatLetter[i] == c.flatLetter[i+1]:
                    c.flatLetter.pop(i+1)
                    c.flatSD.pop(i+1)
                i += 1

    def reduceDuplicatePitches( self ):  # differs from stripDuplicatePitches by allowing a pitch to be duplicated once
    
    # IS IT NECESSARY TO REMOVE PITCHES FROM WORD-BY-WORD REPRESENTATION?
    
        for c in self.chants:
            i = 0
            while i < len(c.flatLetter)-2:
                while c.flatLetter[i] == c.flatLetter[i+1] and c.flatLetter[i] == c.flatLetter[i+2]:
                    c.flatLetter.pop(i+1)
                    c.flatSD.pop(i+1)
                i += 1

    def stripAnticipations( self ):
            
        for c in self.chants:
        
            for wordIndex, w in enumerate(c.words[1:]):
                for syllableIndex, s in enumerate(w.syllables):
            
                    wordIndex = wordIndex+1 # because we're starting with c.words[1] but enumerate starts from 0
            
                    try:
                        thisLetter = s.notes[0].letter
                        if syllableIndex == 0:
                            prevSyllable = c.words[wordIndex-1].syllables[-1]
                        else:
                            prevSyllable = w.syllables[syllableIndex - 1] 
                        prevLetter = prevSyllable.notes[-1].letter
                        syllLength = len(prevSyllable.notes)
            
                        if thisLetter == prevLetter and syllLength > 1:
                            prevSyllable.notes.pop()

                    except IndexError:
                        pass # this only happens in chants with missing notes (c.ignoreMissingNotes = True)

            # reset lazy properties if necessary 
            try:
                del c.flatLetter
            except AttributeError:   
                pass
            try:
                del c.flatSD
            except AttributeError:   
                pass
            try:
                del c.volpiano            
            except AttributeError:
                pass

    def countNotes(self): # count notes in non-ignored chants
        total = 0
        for c in self.chants:
            if c.ignore():
                continue
            for n in c.flatLetter[1:-1]:
                total += 1
        return total
        
    def countChants(self): # count non-ignored chants
        total = 0
        for c in self.chants:
            if c.ignore():
                continue
            total += 1
        return total
    
    def randomTrainingAndTest( self, trainingRatio = .8 ):

        # make a copy of self.chants (call it l) and randomize the order of l
        l = list(self.chants)
        random.shuffle(l)

        # figure out how many go in each, then slice l into two parts

        trainingSize = round(len(l) * trainingRatio)
        trainingSet = l[:trainingSize]
        testSet = l[trainingSize:]

        return (trainingSet, testSet)




   
# COMMENTING OUT THIS LINE PROBABLY BREAKS OLDER CODE 
# corpus = lmloCorpus()



#sys.stderr.write("{}: building suffix tree\n".format(time.asctime()))
#corpus.findLicks(representation = 'letter', treeDepth = 10)
#sys.stderr.write("{}: done\n".format(time.asctime()))

    
#     def printPartialPrefixTree ( self, lick ):
# 
#         def prefixProb ( lick ):
#             n = len(lick)
#             return self.prefixTree[n][lick[1:]][lick[0:1]] * 1. / self.prefixTree[n][lick[1:]]['total']
# 
#         n = len(lick)
#         thePrefixProb = prefixProb(lick)
#         output = ''
#         output += '{:>6d}'.format(self.prefixTree[n][lick[1:]][lick[0:1]])
#         for i in range(n,self.treeDepth+1): output += '    '
#         for c in lick: output += '{:>4}'.format(c)
#         output += '    '
#         output += '{:.2f}'.format(thePrefixProb)
#         if thePrefixProb > self.probThreshold: 
#             output += " *"
#         if output[-1]=='*': print output
#         if lick[0] == startToken or n == self.treeDepth: return
#         for prefix in sorted(self.prefixTree[n+1][lick], key=sortMagic):
#             if prefix == 'total': continue
#             if self.prefixTree[n+1][lick][prefix] >= self.countThreshold:
#                     self.printPartialPrefixTree ( prefix + lick )
# 
#     def printFullPrefixTree (self):
#         for note in sorted(self.prefixTree[2], key=sortMagic):
#             if note == 'total': continue
#             self.printPartialPrefixTree(note)
