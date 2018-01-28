#-*- coding: utf-8 -*-
import os
import pickle
import re
from my_utils import tokenize, asciify
from lxml import etree
import htmlentitydefs


def transformToAlchemySyntax(entryNodes):
	tokenDict = {}
	atoms = []
	trigrams = {}

	ROOT_DIRECTORY=os.path.dirname(os.path.abspath(__file__))
	titleTokensFile = open(os.path.join(ROOT_DIRECTORY,  "../title-tokens.txt"))
	titleTokens = titleTokensFile.read().strip().split("\n")
	titleTokensFile.close()

	nameTokensFile = open(os.path.join(ROOT_DIRECTORY, "../name-tokens.txt"))
	nameTokens = nameTokensFile.read().strip().split("\n")
	nameTokensFile.close()

	maxPos = 0 # Maximale Positionsanzahl
	maxPositions = {} # Anzahl Positionen der einzelnen Zitationen

	fields = ["number", "author", "title", "year", "pages", "comment", "reference", "city", "editor", "material" ]

	punctConstants = {".": "PERIOD", ",": "COMMA", "   ":"INDENTATION"}

	bracketNames = {"[": "LBRACKET", "]": "RBRACKET"}

	bracketStack = []
	#lastBrackets = None

	while len(entryNodes) > 0:
		entryNode = entryNodes[0]
		if 'WorldCatResult' in str(type(entryNode)):
			worldCatNodes = worldCatToMln(entryNode)
			entryNodes.extend(worldCatNodes)
			del entryNodes[0]
			continue
			
			
		entryType = None
		entryPredicates = [] # zusaetzliche Praedikate fuer Zitation
		entryId = entryNode.get("id")
		#if lastBrackets:
		#	atoms.append(lastBrackets.replace("In", "Last"))
		#lastBrackets = None



		#WorldCat
		italicRangeStart = italicRangeEnd = None
		smallCapsRanges = []
		for child in entryNode:
			if child.tag == "text":
				atoms.append("\n\n//#%s: %s"%(entryId, child.text))
			elif child.tag == "tokens":
				tokens = child
			elif child.tag == "smallCapsRanges":
				smallCapsRanges = child
			elif child.tag == "italicRange":
				italicRangeStart = int(child.get("start"))
				italicRangeEnd = int(child.get("end"))

		#WorldCat
		wcOf = entryNode.get("wcOf")
		if wcOf:
			atoms.append("IsWorldCatOf(%s,%s)"%(entryId, wcOf))

		repeatedId = entryNode.get("repeats")
		if repeatedId:
			atoms.append("IsRepeatedBy(%s,%s)"%(repeatedId, entryId))



		atoms.append("HasVolume(%s,%s)"%(entryId,entryNode.get("volume")))

		curTrigram = []
		for token in tokens:
			tokenText=token.text.replace('\\', '\\\\')
			tokenText=tokenText.replace('"', r'\"')
			if tokenText == u"—":
				tokenText = "---"
			tokenText=tokenText.strip(u"—")
			tokenId = int(token.get("id"))

			if tokenText.endswith(":") and len(tokenText.replace(":","")) > 0:
				tokenText = tokenText[:-1]
				atoms.append("FollowedBy(%s,%d,COLON)"%(entryId,tokenId))

			if len(curTrigram) == 3:
				trigrams.setdefault(tuple(curTrigram), []).append((entryId,tokenId-3,tokenId))
				curTrigram.pop(0)

			tokenText = asciify(tokenText)

			curTrigram.append(tokenText.lower())

			tokenDict[tokenText] = None
		
			atoms.append('Token("%s",%d,%s)'%(tokenText, tokenId, entryId))
			
			delimiter = token.get("delimiter")
			if not delimiter:
				continue
			# FEAT: Multiple white spaces
			#if "   " in delimiter:
			#	atoms.append("FollowedBy(%d,%d,INDENTATION)"%(entryId, tokenId))
			#	delimiter = re.sub(r'\s+', '', delimiter)
			#hasDelimiter = False
			# Punkt, Komma


			for char in punctConstants:
				if char in delimiter:
					curTrigram = []
					atoms.append("FollowedBy(%s,%d,%s)"%(entryId, tokenId,punctConstants[char]))
					#hasDelimiter = True
			#if hasDelimiter:
				#atoms.append("HasDelimiter(%d,%d)"%(entryId, tokenId))
			# brackets
			for char in bracketNames:
				if char in delimiter:
					curTrigram = []
					atoms.append("FollowedBy(%s,%d,%s)"%(entryId,tokenId,bracketNames[char]))
					"""if len(bracketStack) > 0 and bracketStack[-1][0] + char == "[]":
							atoms.append("InBrackets(%d,%d,%d)"%(entryId,bracketStack[-1][1],tokenId))
							lastBrackets = atoms[-1]
							#for i in range(bracketStack[-1][1], tokenId + 1):
							#	atoms.append("InsideBrackets(%d,%d)"%(entryId,i))
							bracketStack.pop()
					else:
						bracketStack.append((char, tokenId + 1))"""


			"""for fieldName, charRange in entry.items():
				startPos, endPos = charRange
				if curOffset >= startPos and (curOffset + len(token)) <= endPos:
					pass
					#atoms.append("InField(%d,F%s,%d)"%(curBibNum, fieldName, curPos))
					#Nicht-Zugehoerigkeit zu anderen Feldern
					#for field in fields:
					#	if field != fieldName:
					#		atoms.append("!InField(%d,F%s,%d)"%(curBibNum,field,curPos))"""
			tokenStart = int(token.get("start"))
			tokenEnd = int(token.get("end"))

			if tokenStart >= italicRangeStart and tokenEnd <= italicRangeEnd:
				atoms.append("IsItalic(%s,%s)"%(entryId, tokenId))

			# Kapitaelchen
			for smallCapsRange in smallCapsRanges:
				rangeStart = int(smallCapsRange.get("start"))
				rangeEnd = int(smallCapsRange.get("end"))

				if tokenStart+1 >= rangeStart and tokenEnd <= rangeEnd:
					atoms.append("IsSmallCaps(%s,%s)"%(entryId, tokenId))
					del smallCapsRange
					break

			if int(tokenId) > maxPos:
				maxPos = int(tokenId)
			maxPositions[entryId] = int(tokenId) 


		del entryNodes[0]

	for token in tokenDict:
		if token[0].isupper():
			atoms.append('IsCapital("%s")'%token)
		if len(token) == 1 and token.isalpha():
			atoms.append('IsAlphaChar("%s")'%token)
		elif token.isdigit():
			numeric = int(token)
			if numeric <= 2003:
				atoms.append('IsYear("%s")'%token)
			else:
				atoms.append('IsDigit("%s")'%token) 
		else:
			#if token.lower() in titleTokens: #TitleToken: Token, das auf Titel hinweist (haupts. Funktionswoerter)
			#	atoms.append('IsTitleToken("%s")'%token)
			#if token.lower() in nameTokens:
			#	atoms.append('IsNameToken("%s")'%token)
			if token in  ("Karte", "Karten", "Falttafel", "Falttafeln", "Tafel", "Tafeln", "Photogr", "Photographien", "Dokument", "Dokumente", "Abbildung", "Abb", "Abbildungen", "Fak", "Faks"):
				atoms.append('IsMaterialToken("%s")'%(token))

	"""for token, num in tokenDict.items():
		if len(token) == 1 and token.isalpha():
			atoms.append("IsAlphaChar(T%d)"%num)
		elif token.isdigit():
			numeric = int(token)
			if 1950 <= numeric <= 2011:
				atoms.append("IsYear(T%d)"%num)
			else:
				atoms.append("IsDigit(T%d)"%num) 
		elif token.startswith("[") and token.endswith("]"):
			atoms.append("InsideBrackets(T%d)"%num)
		elif token.startswith("(") and token.endswith(")"):
			atoms.append("InsideParentheses(T%d)"%num)"""

	"""trigramClasses = {} 
	trigramKeys = trigrams.keys()
	for i in range(len(trigramKeys) -1):
		tri1 = trigramsKeys[i]
		for j in range(i+1, len(trigramKeys)):
			tri2 = trigramKeys[j]
			for k in range(3):
				if LD(tri1[k], tri2[k]) > 1:
					break
				trigramClasses.setdefault(tri1,set()).add(tri2)
				trigramClasses.setdefault(tri2,set()).add(tri1)
	del trigramKeys"""

	trigramAtomSet = set()
	for trigram,occurrences in trigrams.items():
		if len(occurrences) < 2:
			continue
		for i in range(len(occurrences)-1):
			tri1,start1,end1 = occurrences[i]
			for  j in range(i+1,len(occurrences)):
				tri2,start2,end2 = occurrences[j]
				if not (tri1.startswith("WC") and tri2.startswith("WC")):
					trigramAtomSet.add("SimilarTitle(%s,%d,%d,%s,%d,%d)"%(tri1,start1,end1,tri2,start2,end2))
					trigramAtomSet.add("SimilarTitle(%s,%d,%d,%s,%d,%d)"%(tri2,start2,end2,tri1,start1,end1))
	atoms.extend(trigramAtomSet)

	#outfile = open("/tmp/alchemytransformer-debug.txt", "w")
	#outfile.write(str(trigrams))
	#outfile.close()

	#Nicht realisierte Positionen sollen ignoriert werden
	for entryId, positions in maxPositions.items():
		#atoms.append("LastPosition(%s,%d)"%(entryId, positions))
		for i in range(positions+1, maxPos+2):
			atoms.append("Empty(%s,%d)"%(entryId, i))
			#atoms.append("!InField(%s,f,%d)"%(entryId, i))

	#Doppelte Kommas: Anfuehrungsstriche
	delete = []
	for i in range(len(atoms)):
		if re.match(r"FollowedBy\(\d+,\d+,COMMA\)", atoms[i]) and atoms[i+1] == atoms[i]:
			delete.append(i)
			delete.append(i+1)
	delete.sort(reverse=True)
	for i in delete:
		del atoms[i]
	return atoms

def getOffsets(entry):
	rawString = entry["raw"]
	offsets = {}
	for fieldName, value in entry.items():
		if fieldName in ("raw", "type"):
			continue
		if type(value) == type(""):
			rawValue = value
		elif type(value) == type({}):
			rawValue = value["raw"]
		else:
			rawValue = value.raw
		try:
			startPos = rawString.index(rawValue)
		except:
			print("EXCEPTION:")
			print("raw: " + rawString)
			print("substring: " + rawValue)
			continue
		offsets[fieldName] = (startPos, startPos + len(rawValue))
	return offsets



##
# Removes HTML or XML character references and entities from a text string.
#
# @param text The HTML (or XML) source text.
# @return The plain text, as a Unicode string, if necessary.

def unescape(text):
	def fixup(m):
		text = m.group(0)
		if text[:2] == "&#":
			# character reference
			try:
				if text[:3] == "&#x":
					return unichr(int(text[3:-1], 16))
				else:
					return unichr(int(text[2:-1]))
			except ValueError:
				pass
		else:
			# named entity
			try:
				text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
			except KeyError:
				pass
		return text # leave as is
	return re.sub("&#?\w+;", fixup, text)

			
def worldCatToMln(worldCatResult):
	tokenSet = set()

	entryTree = etree.fromstring(worldCatResult.entry.xml)
	entryTokenSet = set([token.text for token in entryTree.xpath(".//token")])

	tree = etree.fromstring(worldCatResult.result)	
	nsmap={'a': 'http://www.w3.org/2005/Atom'}
	predicates = []
	entryNodes = []

	for entry in tree.xpath("//a:entry", namespaces=nsmap):
		eid = entry.xpath("./a:id/text()", namespaces=nsmap)[0].split("/")[-1]
		result = entry.xpath("./a:content/text()",namespaces=nsmap)[0]
		result = re.sub("</?p[^>]*>", "", result)
		result = unescape(result).replace(":", " ")

		predicates.append("//WorldCat #%s: %s"%(eid, result))

		italicRangeStart = result.find("<i>")
		result = result.replace("<i>", "")
		italicRangeEnd = result.find("</i>")

		result = result.replace("</i>", "")
		tokens,offsets,delimiters = tokenize(result)

		tokenSet = set(tokens)
		commonTokens = tokenSet.intersection(entryTokenSet)

		relevance = float(len(commonTokens)) / len(tokenSet)
		if relevance < 0.3:
			continue

		entryNode = etree.Element("entry")
		entryNode.set("id", "WC"+eid)
		entryNode.set("volume", "0")
		entryNode.set("wcOf", str(worldCatResult.entry.id))
		entryNode.set("relevance", str(relevance))

		textNode = etree.Element("text")
		textNode.text = result
		entryNode.append(textNode)

		italicRangeNode = etree.Element("italicRange")
		italicRangeNode.set("start", str(italicRangeStart))
		italicRangeNode.set("end", str(italicRangeEnd))
		entryNode.append(italicRangeNode)

		tokensNode = etree.Element("tokens")
		entryNode.append(tokensNode)

		i = 0
		for t,o,d in zip(tokens,offsets,delimiters):
			tokenNode = etree.Element("token")
			tokenNode.set("id", str(i))
			tokenNode.set("start", str(o[0]))
			tokenNode.set("end", str(o[1]))
			tokenNode.set("delimiter", d)
			tokenNode.text = t

			tokensNode.append(tokenNode)

			i+=1

		entryNodes.append(entryNode)

	entryNodes = sorted(entryNodes, key=(lambda x:float(x.get("relevance"))))[:2]
	#tokens = tokenize(text)
	return entryNodes


def LD(s,t):
	s = ' ' + s
	t = ' ' + t
	d = {}
	S = len(s)
	T = len(t)
	for i in range(S):
		d[i, 0] = i
	for j in range (T):
		d[0, j] = j
	for j in range(1,T):
		for i in range(1,S):
			if s[i] == t[j]:
				d[i, j] = d[i-1, j-1]
			else:
				d[i, j] = min(d[i-1, j] + 1, d[i, j-1] + 1, d[i-1, j-1] + 1)
	return d[S-1, T-1]
