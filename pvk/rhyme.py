from music21 import *
import shutil
import re
import time
import numpy as np
import matplotlib.pyplot as plt

# run -i '/Users/pvk/rep/rhyme/python/classifiers.py'
# mbpt = MBPT()
# mbpt.phonologize('woordje')

def addPhonemes(melody):
	flatmelody = melody.flat.notes
	n_notes = len(flatmelody)
	word = ''
	phons = []
	ixs = []
	for i in range(n_notes):
		if flatmelody[i].lyrics:
			if flatmelody[i].lyrics[0].syllabic != 'end' and flatmelody[i].lyrics[0].syllabic != 'single':
				word = word + flatmelody[i].lyrics[0].text
				ixs.append(i)
			elif flatmelody[i].lyrics[0].syllabic == 'single':
				tophonologize = flatmelody[i].lyrics[0].text
				tophonologize = re.sub(r"[ \.,;:]", "", tophonologize)
				#print tophonologize
				phon = mbpt.phonologize(tophonologize)
				#print phon
				accent = "0"
				if len(phon) > 0 and phon[0] == "'" :
					accent = '1'
					phon = phon[1:]	
				phons.append( [i, phon, accent] )
			elif flatmelody[i].lyrics[0].syllabic == 'end':
				word = word + flatmelody[i].lyrics[0].text
				ixs.append(i)
				word = re.sub(r"[ \.,;:]", "", word)
				#print word
				phon = mbpt.phonologize(word).split('-')
				#print phon 
				if len(phon) != len (ixs):
					print "len(phon) != len (ixs): ", word, phon
				else:
					for n in range(len(phon)):
						hyphvoor = ''
						hyphna = ''
						accent = '0'
						if n > 0: hyphvoor = '-'
						if n < len(phon)-1: hyphna = '-'
						if phon[n][0] == "'" :
							accent = '1'
							phon[n] = phon[n][1:]
						phons.append( [ixs[n], hyphvoor+phon[n]+hyphna, accent ] )
				word = ''
				ixs = []
	#now append lyrics to melody
	for l in phons:
		#print l
		flatmelody[l[0]].addLyric(l[1])
		flatmelody[l[0]].addLyric(l[2])

def removeLeftConsonants(syl):
	if len(syl) == 0:
		return syl
	while syl[0] in 'pbtdkgNmnlrfvszSZjxGhwdZ':
		if len(syl) > 1:
			syl = syl[1:]
		else:
			syl = ''
			break
	return syl

#returns two booleans
# rhyme,identical = wordrhymes(worda,wordb)
# if worda==wordb : rhyme = True, identical = True
# if worda rhymes with wordb : rhyme = True, identical = False
# otherwise : rhyme = False, idential = False
def wordrhymes(worda,wordb):
	#print worda,wordb
	if worda == wordb:
		return True,True
	lenshortest = min(len(worda),len(wordb))
	consonantsAndShwa = 'pbtdkgNmnlrfvszSZjxGhwdZ@'
	res = False
	for ix in range(-1,-lenshortest-1,-1):
		if worda[ix] in consonantsAndShwa:
			if worda[ix] == wordb[ix]:
				continue
			else:
				break
		else: #vowel
			if worda[ix] == wordb[ix]:
				res = True
				break
			else:
				res = False
				break
	return res, False


def sylrhymes(syla,sylb):
	if '@' in syla and '@' in sylb:
		return syla == sylb
	else:
		return removeLeftConsonants(syla) == removeLeftConsonants(sylb)

# generates 'AA' 'AB' 'AC' ... 'AZ' 'BA' 'BB' ... ... 'ZZ'
def generateIdentifiers():
	id1 = 'A'
	for ix1 in range(26):
		id2 = 'A'
		for ix2 in range(26):
			yield id1+id2
			id2 = chr(ord(id2)+1)
		id1 = chr(ord(id1)+1)

def getRhyme(sylrhym,ends):
	rhyme = ['False']*len(sylrhym)
	listexpected = generateIdentifiers()
	expected = next(listexpected)
	#print sylrhym
	#get indices of syllables (exluding '')
	sylixs = [ix for ix,_s in enumerate(sylrhym) if sylrhym[ix]!='']
	#pairs = [(sylixs[i], sylixs[i+1]) for i,_s in enumerate(sylixs) if i<len(sylixs)-1]
	for ixix,ix in enumerate(sylixs):
		#print expected, sylrhym[ix]
		if sylrhym[ix]=='':
			continue
		if sylrhym[ix] != expected:
			rhyme[ix] = True
			rhyme[sylrhym.index(sylrhym[ix])] = True #also first occurrence
		else:
			expected = next(listexpected)
	#print rhyme 
	#now make sure that only last 'True' is kept if there are 'True''s in a row
	#for ix in range(1,len(rhyme)):
	#	if rhyme[ix]=='' and ix<len(rhyme) and rhyme[ix+1]==True and rhyme[ix-1]==True:
	#		print ix, rhyme[ix-1], rhyme[ix], ' -> ',
	#		rhyme[ix-1] = False
	#		print rhyme[ix-1], rhyme[ix]
	#	if rhyme[ix]==True and (rhyme[ix-1]==True or sylrhym[ix-1]==''):
	#		print ix, rhyme[ix-1], rhyme[ix], ' -> ',
	#		rhyme[ix-1] = False
	#		print rhyme[ix-1], rhyme[ix]
	#remove 'True' is not at phrase ending
	#for ix in range(len(sylrhym)):
	#	if rhyme[ix] and ends[ix] == 0:
	#		rhyme[ix-1] = False
	#print rhyme
	return rhyme


#expect a song that already has Phonemes and stress as added by addPhonemes(s)
def assignRhymeIdentifiers(s):
	fl = s.flat.notes

	def getend(note):
		if not note.lyrics:
			return -1
		else:
			if note.lyrics[1].syllabic == 'end' or note.lyrics[1].syllabic == 'single':
				return 1
			else:
				return 0

	def getsyl(note):
		if not note.lyrics:
			return ''
		else:
			return note.lyrics[1].text

	syls = list(map(getsyl,fl))
	ends = list(map(getend,fl))
	sylrhym = ['']*len(syls)

	id1 = 'A'
	id2 = 'A'
	for ix1 in range(len(syls)-1):
		if sylrhym[ix1] != '' or syls[ix1] == '':
			continue
		else:
			sylrhym[ix1] = id1+id2
		for ix2 in range(ix1+1,len(syls)):
			if sylrhymes(syls[ix1],syls[ix2]):
				sylrhym[ix2] = id1+id2
		id2 = chr(ord(id2)+1)
		if ord(id2) > 90:
			id1 = chr(ord(id1)+1)
			id2 = 'A'

	#now we have rhyme on syllable level
	#detect rhyme at word / phrase level
	rhyme = getRhyme(sylrhym,ends)

	#for ix in range(len(syls)):
		#print syls[ix], ends[ix], sylrhym[ix], rhyme[ix]

	for ix in range(len(syls)):
		if fl[ix].lyrics:
			fl[ix].addLyric(sylrhym[ix])
			fl[ix].addLyric(str(rhyme[ix]))




#expect a song that already has Phonemes and stress as added by addPhonemes(s)
def collectPhonemeWords(s):
	#collect words
	fl = s.flat.notes
	#fl.show()
	words = []
	word = ''
	for ix, n in enumerate(fl):
		if not n.lyrics: #this is problematic
			continue
		if len(n.lyrics) < 2:
			continue
		word = word + n.lyrics[1].text
		if n.lyrics[1].syllabic == 'single' or n.lyrics[1].syllabic == 'end':
			words.append((word,ix)) #store index of last syllable in word
			word = ''
	return words

def plotboolmatrix(m):
	simbool = np.zeros((len(m),len(m)))
	for i in range(len(m)):
		for j in range(len(m)):
			if m[i][j]==True: simbool[i][j] = 1.0
	plt.imshow(simbool)
	plt.draw()

def detectRhymeWords(words,plot=False):
	#create similaritymatrix
	sim   = [ [ False for i in range(len(words))] for j in range(len(words))]
	ident = [ [ False for i in range(len(words))] for j in range(len(words))]
	for x in range(len(words)):
		for y in range(len(words)):
			rm,idl = wordrhymes(words[x][0],words[y][0])
			#print x, y, words[x][0], words[y][0], rm, idl 
			sim[x][y] = rm
			ident[x][y] = idl
			#print sim,ident
	if plot==True:
		plt.ion()
		plt.show()
		plotboolmatrix(sim)
	#return sim,ident
	# back to front
	# if words rhymes : annotate
	# if words are identical : only last of series identical words rhymes
	rhymes = [False]*len(words)
	for x in range(-1,-len(words)-1,-1):
		for y in range(x-1,-len(words)-1,-1):
			#print words[x], words[y], sim[x][y], ident[x][y]
			#time.sleep(1)
			if sim[x][y] == True:
				rhymes[x] = True
				rhymes[y] = True
				#clear trace
				x1 = x-1
				y1 = y-1
				while (x1 > -len(words)) and (y1 > -len(words)) and (ident[x1][y1] == True):
					sim[x1][y1] = False
					ident[x1][y1] = False
					x1 = x1 - 1
					y1 = y1 - 1
				if plot==True: plotboolmatrix(sim)
	return rhymes

def addRhymeToSong(s,rhymes,words):
	fl = s.flat.notes 
	for n in fl:
		if n.lyrics:
			n.addLyric("False")
	for ix,w in enumerate(words):
		#print ix, w, rhymes[ix], w[1]
		if rhymes[ix]==True:
			fl[w[1]].lyrics[-1].text="True"

def showRhyme(nlbid):
	s = converter.parse('/Users/pvk/Documents/data/Annotated_krn/'+nlbid+'.krn')
	addPhonemes(s)
	words = collectPhonemeWords(s)
	rh = detectRhymeWords(words)
	addRhymeToSong(s,rh,words)
	s.insert(metadata.Metadata())
	s.metadata.title = nlbid
	out = s.write('lily.png')
	shutil.move(out,'/Users/pvk/Documents/Eigenwerk/Projects/Rhyme/png/'+nlbid+'.png')

def showPhonology(nlbid):
	# nlbid : 'NLBxxxxxx_yy'
	# load song
	s = converter.parse('/Users/pvk/Documents/data/Annotated_krn/'+nlbid+'.krn')
	addPhonemes(s)
	s.insert(metadata.Metadata())
	s.metadata.title = nlbid
	out = s.write('lily.png')
	shutil.move(out,'/Users/pvk/Documents/Eigenwerk/Projects/Rhyme/png/'+nlbid+'.png')
