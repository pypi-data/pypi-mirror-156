

import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import re
import os
import string
from nltk import word_tokenize
import nltk
from nltk.stem import WordNetLemmatizer
import json

class Poem:

    full_text = ''
    file_name = ''
    nr_tokens = 0
    nr_types = 0
    nr_stanzas = 0
    nr_lines = 0


    lines = dict()
    transcriptions = dict()


    def __init__(self, file_name ):
        self.file_name = file_name

        nr_lines = 0
        nr_words = 0
        nr_stanzas = 0
        stanza_structure = dict()

        tokens_count = 0
        if re.search( r'\.xml$' , self.file_name ):
            try:

                ns = {'tei': 'http://www.tei-c.org/ns/1.0' }

                with open( file_name , encoding = 'utf-8' ) as file:
                    xml = file.read()

                root = ET.fromstring(xml)
                tei_text = root.find('tei:text/tei:body' , ns )
                stanzas = tei_text.findall('tei:lg' , ns )

                line_elements = []
                full_text = dict()
                transcriptions = dict()
                breaks = []

                if len(stanzas) > 0:
                    nr_stanzas = len(stanzas)
                    for s in stanzas:
                        breaks.append( nr_lines + 1 )
                        lines = s.findall('tei:l' , ns )
                        for l in lines:
                            nr_lines += 1
                            line_elements.append(l)
                else:
                    lines = tei_text.findall('tei:l' , ns )
                    for l in lines:
                        nr_lines += 1
                        line_elements.append(l)

                for l in line_elements:
                    n_line = l.get('n')
                    n_line = int(n_line)
                    line_text = ''
                    transcription = ''
                    words = l.findall('tei:w' , ns )
                    for w in words:
                        if re.search( r'\w+', str(w.text) ):
                            line_text += ' '
                        line_text += w.text
                        transcription += w.get('phon') + ' '
                    full_text[ n_line ] = line_text.strip()
                    transcriptions[ n_line ] = transcription.strip()
                    words = word_tokenise( full_text[ n_line ] )
                    nr_words += len(words)

            except:
                print( "Cannot read " + self.file_name + " !" )

            self.lines = full_text
            self.nr_words = nr_words
            self.nr_stanzas = nr_stanzas
            self.nr_lines = nr_lines

            structure = dict()

            stanza_count = 0
            stanza_lines = []
            for i in range(1, nr_lines+1):
                if i in breaks:
                    if len(stanza_lines) > 0:
                        stanza_count += 1
                        structure[stanza_count] = stanza_lines
                        stanza_lines = []
                stanza_lines.append(i)
            if len(stanza_lines) > 0:
                stanza_count += 1
                structure[stanza_count] = stanza_lines
                stanza_lines = []

            self.stanza_structure = structure


            complete_full_text = ''
            for l in full_text:
                complete_full_text += full_text[l] + ' '
            self.full_text = complete_full_text.strip()
            self.transcriptions = transcriptions

            title = os.path.basename( self.file_name )
            title = re.sub( r'[.]txt$' , '' , title )
            title = re.sub( r'[.]xml$' , '' , title )
            title = re.sub( r'_' , ' ' , title )
            # So that it can be used in CSV files
            title = re.sub( r',' , ' ' , title )
            self.title = title

    def __str__(self):
        return f'The contents of { self.file_name }'


    def tokens( self ):
        return self.tokens

    def texture(self):

        svg = ''
        html = ''

        transcr = self.transcriptions
        lines = self.lines

        last_lines = []
        struct = self.stanza_structure
        for s in struct:
            last_lines.append(struct[s][-1])


        for n in lines:

            phonemes = separatePhonemes( transcr[n] )
            panel_length = len(phonemes) * 16 + 10

            svg = f'<svg width = "{panel_length}" height="18">'

            for i,sound in enumerate(phonemes):
                # determine colour
                colour = find_colour(sound)
                #colour = '#FF0099'
                svg += f'<rect x={i*16} , y={2} , width="12" height="10" style="fill:{colour}" />'

            svg += '</svg>'
            html += svg + '<br/>'
            if n in last_lines:
                html += '<br/>'

        return html


    def visualise_rhyme_alliteration(self):

        lines = self.transcriptions
        max_words = 0
        rhymes_lines = []
        stanzas = self.stanza_structure
        nr_stanzas = len(stanzas)
        last_lines = []

        for s in stanzas:
            stanza_lines = []
            for n in stanzas[s]:
                stanza_lines.append(lines[n])
            last_lines.append(stanzas[s][-1])

            rhyming_scheme = perfect_rhyme(stanza_lines)
            rhyming_scheme = re.sub( r'\s+' , '' , rhyming_scheme )
            for c in rhyming_scheme:
                rhymes_lines.append(c)


        for l in lines:
            words = word_tokenise(lines[l])
            if len(words) > max_words:
                max_words = len(words)

        line_height = 30
        word_width = 40
        space_after_stanza = 30

        panel_width = max_words * word_width + 10
        panel_height = len(lines) * line_height + 10
        panel_height += nr_stanzas * space_after_stanza

        stanza_offset = 0

        svg = f'<svg width = "{panel_width}" height="{panel_height}">'


        for i,l in enumerate(lines):
            if i in last_lines:
                stanza_offset += space_after_stanza
            alliteration_pattern = alliteration(lines[l])
            alliteration_words = re.split( r'\s+' , alliteration_pattern.strip() )
            words = word_tokenise(lines[l])
            for j,w in enumerate(words):
                colour = '#d4cccb'
                colour2 = '#ed4934'
                colour3 = '#4b8efa'
                svg+= f'<rect x={j*word_width} , y={i*line_height + stanza_offset} , width="{word_width-5}" height="{line_height-20}" style="fill:{colour}" />'
                if re.search( r'\w' ,  alliteration_words[j] ):
                    svg+= f'<rect x={j*word_width} , y={i*line_height + line_height-20 + stanza_offset} , width="{(word_width-5)}" height="{(line_height-20)/2}" style="fill:{colour2}" />'
            if re.search( r'\d' , rhymes_lines[i] ):

                if re.search( r'\w' ,  alliteration_words[-1] ):

                    y = line_height-15
                else:
                    y = line_height-20
                svg+= f'<rect x={j*word_width} , y={i*line_height + y + stanza_offset} , width="{(word_width-5)}" height="{(line_height-20)/2}" style="fill:{colour3}" />'

        svg += '</svg>'
        return svg

    def show_perfect_rhyme(self , show_lines = True ):
        # Mainly for demonstration purposes
        lines = self.lines
        tr = self.transcriptions

        stanzas = self.stanza_structure
        for s in stanzas:
            stanza_lines = []
            for n in stanzas[s]:
                stanza_lines.append(tr[n])

            rhyming_scheme = perfect_rhyme(stanza_lines)
            if show_lines:
                for n in stanzas[s]:
                    print(lines[n])
            print(rhyming_scheme)
            print('\n', end = '')



    def show_slant_rhyme_assonance(self , show_lines = True ):
        # Mainly for demonstration purposes
        lines = self.lines
        tr = self.transcriptions

        stanzas = self.stanza_structure
        for s in stanzas:
            stanza_lines = []
            for n in stanzas[s]:
                stanza_lines.append(tr[n])

            rhyming_scheme = slant_rhyme_assonance(stanza_lines)
            if re.search( r'\d' , rhyming_scheme ):
                if show_lines:
                    for n in stanzas[s]:
                        print(lines[n])
                print(rhyming_scheme)

    def show_slant_rhyme_consonance(self , show_lines = True ):
        # Mainly for demonstration purposes
        lines = self.lines
        tr = self.transcriptions

        stanzas = self.stanza_structure
        for s in stanzas:
            stanza_lines = []
            for n in stanzas[s]:
                stanza_lines.append(tr[n])

            rhyming_scheme = slant_rhyme_consonance(stanza_lines)
            if re.search( r'\d' , rhyming_scheme ):
                if show_lines:
                    for n in stanzas[s]:
                        print(lines[n])
                print(rhyming_scheme)

    def show_alliteration(self ):

        transcr = self.transcriptions
        lines = self.lines
        pattern = ''

        for n in transcr:
            pattern = alliteration(transcr[n])

            if re.search( r'\w' , pattern):
                print(lines[n])
                print( pattern )
                print( '\n' , end='')

    def show_internal_rhyme(self):
        transcr = self.transcriptions
        lines = self.lines
        pattern = ''

        for n in transcr:
            pattern = internal_rhyme(transcr[n])
            if len(pattern)>0:
                print( lines[n] )
                print( pattern )
                print( '\n' , end='')

    def anaphora_count_lines(self):

        count = 0
        lines = self.lines

        a = anaphora(lines.values())
        if len(a) > 0:

            for l in lines.values():
                for ra in a:
                    if re.search( '^{}'.format(ra) , l.lower() ):
                        count += 1
        return( count )






# function to tokenise a string into words
def word_tokenise( text ):
    tokens = []
    #text = text.lower()
    text = re.sub( '--' , ' -- ' , text)
    words = re.split( r'\s+' , text )
    for w in words:
        if re.search( r"(\w)|(@)" , w ):
            tokens.append(w)
    return tokens

def transcribe( line ):
    read_dictionary()
    words = word_tokenise( line )
    full_transcription = ''
    for word in words:
        word = word.strip( string.punctuation )
        word = re.sub( r'(\’)' , '\'' , word )
        word = re.sub( r'^[\’\';:\"]' , '' ,  word )
        word = re.sub( r'[\’\';:\"]$' , '' , word )
        transcription = pronunciation_dict.get( word.lower() , "" ) + ' '
        if not re.search( r'\w' , transcription ):
            if re.search( r'-' , str(word) ):

                constituents = re.split( r'-' , word )
                for i,c in enumerate(constituents):
                    transcription += pronunciation_dict.get( c.lower() , "" )
                    if i < len(constituents)-1:
                        transcription += '-'
            if re.search( r'\'s$' , str(word) ):
                word = re.sub( r'\'s$' , '' , word )
                transcription = pronunciation_dict.get( word.lower() , "" )
                transcription += 'z'
        full_transcription += transcription + ' '
    full_transcription = re.sub( r'\s+' , ' ' , full_transcription )
    return full_transcription.strip()

def missing_words( line ):
    read_dictionary()
    words = word_tokenise( line )
    missing = []
    transcription = ''
    for word in words:
        transcription = transcribe(word)
        if not re.search( r'\w' , transcription ):
            missing.append(word)
    return missing


consonants = "b|c|d|f|g|h|j|k|l|m|n|p|q|r|s|t|v|w|x|z|D|Z|S|T|N"
vowels = "{|@|V|I|e|Q|U"
diphthongs = "aU|@U|A:|3:|i:|u:|O:|eI|aI|oI|@U|e@|I@|U@|dZ|tS"


def separatePhonemes( text ):
    phonemes = []
    text = re.sub( r'\s+' , '' , text )
    text = re.sub( r'!' , '' , text )
    text = re.sub( r'%' , '' , text )

    consonants = "b|d|f|g|h|j|k|l|m|n|p|r|s|t|v|w|z|S|Z|D|T"
    vowels = "{|@|V|I|e|Q|U"

    regex = r'aU|@U|A:|3:|i:|u:|O:|eI|aI|oI|@U|e@|I@|U@|dZ|tS'
    regex += '|[{}]'.format(consonants)
    regex += '|[{}]'.format(vowels)

    phonemes = re.findall( regex , text )
    return phonemes


def finalPhonemeSequence( text ):
    rhyme = finalStressedSyllable( text )
    rhyme = re.sub( r'^[{}]+'.format(consonants) , '' , rhyme )
    return rhyme


def finalPhonemeSequence_line( line ):
    words = re.split( r'\s+' , line )
    last_word = words[-1]
    fps = finalPhonemeSequence(last_word)
    return fps

def finalStressedSyllable( word ):
    word = re.sub( r'(\*)|(%)' , '!' , word )
    parts = re.split( r'!' , word )
    rhyme = parts[-1]
    rhyme = re.sub( r'!' , '' , rhyme )
    rhyme = re.sub( r'-' , '' , rhyme )
    rhyme = re.sub( r'\s+' , '' , rhyme )
    return rhyme

def is_vowel( phoneme ):

    regex = r'{}|{}'.format( diphthongs , vowels )

    if re.search( regex , phoneme ):
        return True
    else:
        return False

def is_consonant( phoneme ):

    if re.search( r'[{}]'.format(consonants) , phoneme ):
        return True
    else:
        return False



def ptb_to_wordnet(PTT):

    if PTT.startswith('J'):
        ## Adjective
        return 'a'
    elif PTT.startswith('V'):
        ## Verb
        return 'v'
    elif PTT.startswith('N'):
        ## Noune
        return 'n'
    elif PTT.startswith('R'):
        ## Adverb
        return 'r'
    else:
        return ''


lemmatiser = WordNetLemmatizer()


## Read pronunication dictionary
pronunciation_dict = dict()


tei_start = '''<?xml version="1.0" encoding="UTF-8"?>
<?xml-model href="../tei_lite.rng" type="application/xml" schematypens="http://relaxng.org/ns/structure/1.0"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
  <teiHeader>
      <fileDesc>
         <titleStmt>
            <title>##TITLE##</title>
         </titleStmt>
         <publicationStmt>
            <p>Publication Information; to be added</p>
         </publicationStmt>
         <sourceDesc>
            <p>##TITLE##</p>
         </sourceDesc>
      </fileDesc>
  </teiHeader><text>
      <body>'''

tei_end =	'''</body>
		   </text>
		</TEI>
		'''


def encodeFileName(text):
	text = re.sub( r'[\'`]' , '&#x27;' , text)
	text = re.sub( r'\s+' , '_' , text)
	return text



def encode_line(line):
    encoded_line = ''
    words = word_tokenise(line)
    pos = nltk.pos_tag(words)
    for i in range( 0 , len(words) ):
        if re.search( r'\w' , words[i] ):
            encoded_line += '\n<w '
            word = words[i]
            encoded_line += f'pos="{pos[i][1]}" '
            lemma = ''
            posTag = ptb_to_wordnet( pos[i][1] )


            if re.search( r'\w+' , posTag , re.IGNORECASE ):
                lemma = lemmatiser.lemmatize( words[i] , posTag )
            else:
                lemma = lemmatiser.lemmatize( words[i] )

            if re.search( r'—' , lemma ):
                lemma = re.sub( r'—' , '' , lemma )
            lemma = lemma.strip( string.punctuation ).lower()



            encoded_line += f'lemma="{lemma}" '
            transcr = transcribe(word)
            transcr = re.sub( r'["]' , '!' , transcr )
            encoded_line += f'phon="{ transcr  }" '
            encoded_line += '>'
            encoded_line += f'{ word }</w> '
        else:
            encoded_line = encoded_line.strip() + words[i]
    return encoded_line


def read_dictionary():

    if len(pronunciation_dict) == 0:
        try:
            import importlib.resources as pkg_resources
        except ImportError:
            import importlib_resources as pkg_resources

        data = pkg_resources.read_text( 'reading_poetry' , 'pronunciationDictionary.json')

        json_data = json.loads(data)
        for w in json_data:
            pronunciation_dict[ w['word'] ] = w['transcription']


def add_annotations(file_name):

    read_dictionary()

    print( f'Adding annotations for {file_name} ... ')

    # open file
    with open( file_name , encoding  = 'utf-8') as fh:
    	full_text = fh.read()
    	full_text = full_text.strip()

    # get verse lines
    segments = re.split( r'\n' , full_text )
    # We assume that the first line contains the title
    title = segments[0]
    del segments[0]

    if re.search( r'\w' , segments[0]):
        segments.insert(0,'')

    lines = dict()
    n_line = 0
    n_stanza = 0
    open_stanza = False

    body = ''
    for index in range( 0 , len(segments) ):
        line = segments[index]

        if re.search( r'\w' , line):
            ## remove entities
            line = re.sub( r'&\w+;' , '' , line )
            n_line += 1
            body += f'\n<l n="{n_line}">{ encode_line(line) }</l>'
        else:
            if n_line > 0:
                body += '</lg>'
            n_stanza += 1
            body += f'\n<lg n="s{n_stanza}">'

    body += '\n</lg>'


    tei_header = re.split('##TITLE##' , tei_start)

    tei_full = tei_header[0]
    tei_full += title
    tei_full += tei_header[1]
    tei_full += title
    tei_full += tei_header[2]
    tei_full += f'<head><title>{title}</title></head>'
    tei_full += body
    tei_full += tei_end

    return tei_full




## Literary devices

def alliteration(tr_line):
    scheme = ''
    sounds_start = dict()
    alliterations = []

    pattern_list = []
    words = re.split( r'\s+' , tr_line )

    for w in words:
        if re.search( r'!' , w):
            syllables = re.split( '-' , w )
            for s in syllables:
                if re.search( r'^!' , s):
                    phonemes = separatePhonemes(s)
                    if len(phonemes)>0:
                        pattern_list.append( phonemes[0] )
                        sounds_start[ phonemes[0] ] = sounds_start.get( phonemes[0] , 0) +1
        else:
            pattern_list.append( '-' )

    for s in sounds_start:
        if sounds_start[s] > 1:
            alliterations.append(s)

    pattern = ''
    for p in pattern_list:
        if p in alliterations:
            pattern += f'{p} '
        else:
            pattern += '- '

    return pattern



## Rhyme

def perfect_rhyme( stanza ):
    # input: list of transcibed lines
    # these lines form a stanza

    # dict used to tarce repeated words
    ## repeated words are not rhymes
    word_count = dict()
    sounds_freq = dict()
    stanza_pattern = []

    for l in stanza:


        fps = finalPhonemeSequence(l)
        words = word_tokenise(l)

        stressed_words = []
        for w in words:
            if re.search( r'(!)|(%)|(\*)' , w ):
                stressed_words.append(w)
        if len(stressed_words) > 1:
            last_word = stressed_words[-1]
        elif len(words) > 0:
            last_word = words[-1]
        else:
            last_word = l

        ## fuzzy matching
        if re.search( r's$' , fps ):
            fps = re.sub( r's$', 'z^' , fps )
        if re.search( r'd$' , fps ):
            fps = re.sub( r'd$', 't' , fps )
        if re.search( r'I@' , fps ):
            fps = re.sub( r'I@', 'i:' , fps )

        consonants = "bdfghjklmnprstvwzSZDT"
        regex = f'-([{consonants}]+)@([{consonants}]+)$'
        if re.search( r'{}'.format(regex) , fps ):

            match = re.search( r'{}'.format(regex) , fps )

            pattern1 = match.group(1)
            pattern2 = match.group(2)
            replace = '-'+pattern1+pattern2
            fps = re.sub( r'{}'.format(regex) , replace , fps )

        ## repeated words are not rhymes
        word_count[last_word] = word_count.get( last_word , 0) + 1
        ## final phoneme sequences are saved in a list
        if word_count[last_word] == 1:
            sounds_freq[fps] = sounds_freq.get(fps,0)+1
            stanza_pattern.append(fps)
        else:
            stanza_pattern.append('-')

        rhyming_scheme = ''
        code = 0
        code_dict = dict()
        for line in stanza_pattern:
            #assign code to repeated sound
            if sounds_freq.get(line,0) > 1 and line not in code_dict:
                code += 1
                code_dict[line] = code

            if line in code_dict:
                rhyming_scheme += str(code_dict[line]) + ' '
            else:
                rhyming_scheme += '- '

    return rhyming_scheme



def line_ending(line):

    fps = finalPhonemeSequence_line(line)
    if re.search( r'-' , fps ):
        return 'F'
    else:
        return 'M'



def internal_rhyme( line ):
    internal_rhymes = []

    sounds_freq = dict()
    words = re.split( r'\s+' , line )

    ## deduplicate the words
    words = list( set(words) )
    stopwords = ['!aI','!D{t',"D@","@","!D@U","Q"]
    for w in words:
        if w in stopwords:
            words.remove(w)

    for word in words:

        fps = finalPhonemeSequence(word)

        sounds_freq[fps] = sounds_freq.get(fps,0) + 1

    for s in sounds_freq:
        if sounds_freq[s] > 1:
            internal_rhymes.append(s)

    return internal_rhymes



def slant_rhyme_consonance( stanza ):

    # agreement in the consonants of final phoneme sequence

    stanza_pattern = []
    sounds_freq = dict()
    words_freq = dict()
    word_pattern = dict()

    for l in stanza:
        words = re.split( r'\s+' , l )
        last_word = words[-1]

        phonemes = separatePhonemes(last_word)
        # pattern which represents consonants of final word
        pattern = ''
        for ph in phonemes:
            if is_vowel(ph):
                pattern += '-'
            else:
                pattern += ph

        ## connect word to pattern
        word_pattern[last_word] = pattern

        # count patterns
        sounds_freq[ pattern ] = sounds_freq.get( pattern , 0 ) + 1
        words_freq[ last_word ] = words_freq.get( last_word , 0 ) + 1
        # create pattern for stanza
        stanza_pattern.append(last_word)

    rhyming_scheme = ''
    code = 0
    code_dict = dict()
    for line in stanza_pattern:
        pattern = word_pattern[line]

        if words_freq[line] == 1 and sounds_freq.get(pattern,0) > 1:
            # the word occurs only once and the sound more than once

            # assign code to pattern
            if pattern not in code_dict:
                code += 1
                code_dict[pattern] = code

        if pattern in code_dict:
            # this implies that the sound occurs more than once
            rhyming_scheme += str(code_dict[pattern]) + ' '
        else:
            rhyming_scheme += '- '

    return rhyming_scheme

def slant_rhyme_assonance( stanza ):
    pr = perfect_rhyme(stanza)
    pr = re.sub( r'\s+' , '' , pr)

    pr_lines = [char for char in pr]


    new_stanza = []
    rhyming_sounds = []
    for i,line in enumerate(stanza):
        if pr_lines[i] == '-':
            new_stanza.append(line)
        else:
            if pr_lines[i] not in rhyming_sounds:
                new_stanza.append(line)
                rhyming_sounds.append(pr_lines[i])


    stanza_pattern = []
    sounds_freq = dict()

    for l in new_stanza:
        # tokenise line and find phoneme sequence
        # after last stressed syllable
        words = re.split( r'\s+' , l )
        fps = finalPhonemeSequence(l)

        # create pattern representing vowels
        phonemes = separatePhonemes(fps)
        pattern = ''
        for ph in phonemes:
            if is_consonant(ph):
                pattern += '-'
            else:
                pattern += ph

        # Fuzzy matching
        pattern = re.sub( r'@U' , 'Q' , pattern )
        #I and i: ?

        pattern = re.sub( r'-+' , '-' , pattern )
        pattern = re.sub( r'^-' , '' , pattern )
        #print(pattern)
        stanza_pattern.append(pattern)
        sounds_freq[ pattern ] = sounds_freq.get( pattern , 0 ) + 1

    rhyming_scheme = ''
    code = 0
    code_dict = dict()

    for pattern in stanza_pattern:


        if sounds_freq.get(pattern,0) > 1:

            if pattern not in code_dict:
                code += 1
                code_dict[pattern] = code

        if pattern in code_dict:
            rhyming_scheme += str(code_dict[pattern]) + ' '
        else:
            rhyming_scheme += '- '

    return rhyming_scheme









def slant_rhyme_assonance2( stanza ):

    stanza_pattern = []
    sounds_freq = dict()
    perfect_rhyme = dict()
    words_freq = dict()
    fps_freq = dict()
    word_pattern = dict()

    for l in stanza:
        # tokenise line and find last word
        words = re.split( r'\s+' , l )
        # find final phoneme sequence
        fps = finalPhonemeSequence(l)

        fps_freq[last_word] = fps_freq.get(last_word,0) +1
        words_freq[ last_word ] = words_freq.get( last_word , 0 ) + 1
        stanza_pattern.append(last_word)

        if words_freq[last_word] == 1:
            perfect_rhyme[fps] = perfect_rhyme.get(fps,0)+1

        # create pattern representing vowels
        phonemes = separatePhonemes(last_word)
        pattern = ''
        for ph in phonemes:
            if is_consonant(ph):
                pattern += '-'
            else:
                pattern += ph

        # Fuzzy matching
        pattern = re.sub( r'@U' , 'Q' , pattern )
        #I and i: ?

        pattern = re.sub( r'-+' , '-' , pattern )
        pattern = re.sub( r'^-' , '' , pattern )
        #print(pattern)
        word_pattern[last_word] = pattern
        sounds_freq[ pattern ] = sounds_freq.get( pattern , 0 ) + 1

    # Ignore the perfect rhymes
    # instances of perfect rhymes deduced
    # from counts for slant rhyme
    for r in perfect_rhyme:
        if perfect_rhyme[r] > 1:
            phonemes = separatePhonemes(r)
            pattern = ''
            for ph in phonemes:
                if is_consonant(ph):
                    pattern += '-'
                else:
                    pattern += ph


            for sound in sounds_freq:
                if re.search( r'{}$'.format(pattern) , sound ):
                    sounds_freq[sound] = sounds_freq[sound] - (perfect_rhyme[r] -1)

    rhyming_scheme = ''
    code = 0
    code_dict = dict()
    for line in stanza_pattern:
        pattern = word_pattern[line]

        if words_freq[line] == 1 and sounds_freq.get(pattern,0) > 1:

            if pattern not in code_dict:
                code += 1
                code_dict[pattern] = code

        if pattern in code_dict:
            rhyming_scheme += str(code_dict[pattern]) + ' '
        else:
            rhyming_scheme += '- '

    return rhyming_scheme


def anaphora(stanza):

    lines_words = []
    max_words = 0
    for l in stanza:
        l = re.sub( r'[.;:,!"\']' , '' , str(l) )
        words = word_tokenise(l.lower())
        if len(words) > max_words:
            max_words = len(words)
        lines_words.append(words)


    all_bigrams = []

    while max_words > 1 and len(all_bigrams) == 0:
        bigrams = dict()
        for l in lines_words:
            b = ' '.join(l[:max_words])
            b = re.sub( r'[.;:,!"\']' , '' , str(b) )
            bigrams[b] = bigrams.get(b,0)+1

        for b in bigrams:
            if bigrams[b] > 1:
                all_bigrams.append(b)


        max_words -= 1

    return all_bigrams



def semi_rhyme( stanza ):

    word_count = dict()
    sounds_freq = dict()
    stanza_pattern = []

    for line in stanza:
        words = re.split( r'\s+' , line )
        last_word = words[-1]
        fps = finalPhonemeSequence( last_word )
        if re.search( r'-' , fps ):
            print(fps)
            fps = fps[ : fps.index('-') ]
            print(fps)

        word_count[last_word] = word_count.get( last_word , 0) + 1
        if word_count[last_word] == 1:
            sounds_freq[fps] = sounds_freq.get(fps,0)+1
            stanza_pattern.append(fps)
        else:
            stanza_pattern.append('-')


        rhyming_scheme = ''
        code = 0
        code_dict = dict()
        for line in stanza_pattern:
            if sounds_freq.get(line,0) > 1 and line not in code_dict:
                code += 1
                code_dict[line] = code

            if line in code_dict:
                rhyming_scheme += str(code_dict[line]) + ' '
            else:
                rhyming_scheme += '- '

    return rhyming_scheme





def find_colour(phon):
    colour = '#FFFFFF'

    # Plosives - Shades of dark blue
    if phon == "p":
        colour = "#0b239d"
    elif phon == "b":
        colour = "#3656f7"
    elif phon == "t":
        colour = "#233485"
    elif phon == "d":
        colour = "#7daef7"
    elif phon == "k":
        colour = "#0723ab"
    elif phon == "g":
        colour = "#5994ee"

    #  Affricatives - Shades of dark red
    elif phon == "tS":
        colour = "#8a1104"
    elif phon == "dZ":
        colour = "#ad2213"

    # fricatives - Shades of light red
    elif phon == "f":
        colour = "#d30326"
    elif phon == "v":
        colour = "#fb042d"
    elif phon == "h":
        colour = "#f10e34"
    elif phon == "T":
        colour = "#e7183b"
    elif phon == "D":
        colour = "#f40b32"

    # Sibilant sounds - shades of green
    elif phon == "s":
        colour = "#0b7314"
    elif phon == "z":
        colour = "#12b320"
    elif phon == "S":
        colour = "#13781c"
    elif phon == "Z":
        colour = "#1ba627"

    # Sonorant sounds - Shades of dark orange
    elif phon == "m":
        colour = "#e37507"
    elif phon == "n":
        colour = "#ef8c2a"
    elif phon == "N":
        colour = "#e68c33"
    elif phon == "r":
        colour = "#f68c23"
    elif phon == "l":
        colour = "#df8c3a"
    elif phon == "w":
        colour = "#f08c28"
    elif phon == "j":
        colour = "#ef9728"

    # vowels - shades of light yellow
    elif phon == "I":
        colour = "#f0eb67"
    elif phon == "e":
        colour = "#f5efbc"
    elif phon == "{":
        colour = "#fbf4b6"
    elif phon == "Q":
        colour = "#FFFDD0"
    elif phon == "V":
        colour = "#f5f0bc"
    elif phon == "U":
        colour = "#fdf8ce"
    elif phon == "@":
        colour = "#F5F5DC"
    elif phon == "i:":
        colour = "#FFBF00"

    # long vowels - Shades of orange
    elif phon == "eI":
        colour = "#f4cd0b"
    elif phon == "aI":
        colour = "#f5d42e"
    elif phon == "OI":
        colour = "#edcf35"
    elif phon == "u:":
        colour = "#e7ca3c"
    elif phon == "@U":
        colour = "#ebd35c"
    elif phon == "aU":
        colour = "#fddf49"
    elif phon == "3:":
        colour = "#fdd50d"
    elif phon == "A:":
        colour = "#f6d013"
    elif phon == "O:":
        colour = "#f8d630"
    elif phon == "I@":
        colour = "#f8ce35"
    elif phon == "e@":
        colour = "#f9d862"
    elif phon == "U@":
        colour = "#f4d567"


    return colour
