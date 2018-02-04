import argparse
import csv
import logging
from multiprocessing import Pool
import os

import mongo_client
from paragraph.paragraph_extraction import extract_paragraphs
from paragraph.type_detection import detect_paragraph_types
from citation_isolated.assembly import assemble_citations
from citation_isolated.citation_parsing import CitationParser


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--full', action='store_true', help='Run full pipeline')
    parser.add_argument('--import', dest='import_paragraphs', action='store_true', default=False,
                        help='Import paragraphs from OCR')
    parser.add_argument('--ocr-files', default='../../data/ocr/TA*.xml', nargs='*', help='Location of OCR directory')
    parser.add_argument('--types', action='store_true', help='Detect entry types')
    parser.add_argument('--category-file', default='../../data/TA_Kategorien_Endschema.csv',
                        help='Path to category CSV')
    parser.add_argument('--find-authors', action='store_true')
    parser.add_argument('--verbose', '-v', action='store_true')

    args = parser.parse_args()

    setup_logging(args.verbose)

    database = mongo_client.get_database('ta')
    if args.full:
        run_full_pipeline(args.ocr_files, args.category_file, database)
        return

    if args.import_paragraphs:
        write_paragraphs_to_database(args.ocr_files, database)
    if args.types:
        category_mapping = get_category_mapping(args.category_file)
        detect_paragraph_types(database, category_mapping)
    if args.find_authors:
        known_authors = set([author.strip() for author in database.citations.distinct('authors') if author])
        citations = database.citations.find({'authors': None, 'fullyParsed': False})
        parser = CitationParser()
        for count, citation in enumerate(parser.find_known_authors(citations, known_authors)):
            if citation.get('authors'):
                citation = parser.parse_citation(citation)
                database.citations.save(citation)
        logging.info('Found known authors in %d citations', count+1)


def run_full_pipeline(ocr_files, category_file, database, drop_existing=True):
    category_mapping = get_category_mapping(category_file)
    if drop_existing:
        database.paragraphs.drop()
        database.citations.drop()

    with Pool(processes=8) as pool:
        pool.starmap(run_full_pipeline_on_volume, [(volume_filename, category_mapping) for volume_filename in ocr_files])

    #do stuff
    logging.info('Creating indexes')
    database.citations.create_index([('volume', 1)])
    database.citations.create_index([('number', 1)])
    database.citations.create_index([('authors', 1)])
    database.citations.create_index([('fullyParsed', 1)])


def run_full_pipeline_on_volume(volume_filename, category_mapping):
    parser = CitationParser()
    logging.info("Processing %s...", volume_filename)

    logging.debug('Extracting paragraphs...')
    paragraphs = extract_paragraphs(volume_filename)

    logging.debug('Determining paragraph types...')
    typed_paragraphs = list(detect_paragraph_types(paragraphs, category_mapping))
    for paragraph in typed_paragraphs:
        paragraph['styles'] = list(paragraph['styles'].items())

    logging.debug('Connecting to database...')
    database = mongo_client.get_database('ta')

    logging.debug('Writing paragraphs to database...')
    database.paragraphs.insert_many(typed_paragraphs)

    logging.debug('Assembling citations...')
    raw_citations = assemble_citations(typed_paragraphs)

    logging.debug('Parsing citations...')
    citations = [parser.parse_citation(raw_citation) for raw_citation in raw_citations]

    if citations:
        logging.debug('Writing {} citations to database...'.format(len(citations)))
        database.citations.insert_many(citations)
    else:
        logging.warning('No citations found.')
    logging.info('Processing of %s done.', volume_filename)



def get_category_mapping(file_name):
    with open(file_name, encoding='utf-8') as category_file:
        reader = csv.reader(category_file, delimiter=';')
        category_mapping = dict(reader)
        return category_mapping


'''def detect_entry_types(database, category_mapping):
    logging.info('Detecting entry types...')
    for volume in database.paragraphs.distinct('volume'):
        volume_paragraphs = database.paragraphs.find({'volume': volume}).sort(
            [('volume', pymongo.ASCENDING), ('index', pymongo.ASCENDING)])
        type_mapping = detect_entry_types(volume_paragraphs, category_mapping)
        for paragraph_id, paragraph_type in type_mapping.items():
            database.paragraphs.update_one({'_id': paragraph_id}, {'$set': {'type': paragraph_type}})
    database.paragraphs.create_index([('type', 1)])'''


def write_paragraphs_to_database(ocr_input_folder, database, drop_existing=True):
    if drop_existing:
        database.paragraphs.drop()
    volume_filenames = [os.path.join(ocr_input_folder, fileName) for fileName in os.listdir(ocr_input_folder) if
                        fileName.startswith("TA") and fileName.endswith(".xml")]
    volume_filenames.sort()
    for volume_filename in volume_filenames:
        print("Processing %s..." % volume_filename)
        paragraphs = extract_paragraphs(volume_filename)
        database.paragraphs.insert_many(list(paragraphs))
    database.paragraphs.create_index([('volume', 1)])


def setup_logging(verbose):
    # set up logging to file - see previous section for more details
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(processName)s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M',
                        filename='/tmp/ta_processing.log',
                        filemode='w')
    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG if verbose else logging.INFO)
    # set a format which is simpler for console use
    formatter = logging.Formatter('[%(asctime)s][%(levelname)s][%(processName)s] %(message)s')
    # tell the handler to use this format
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)


if __name__ == '__main__':
    main()

"""from wordmlparser.wmlparser import WMLParser
from lineparsers.lineparser import LineParser

from lineparsers.lineparserta18 import LineParserTa

from alchemytransformer import transformToAlchemySyntax, getOffsets

#wmlp = WMLParser("../input/TA01_02_Xhosa_WML_formatted_pb_nopic_patterns.xml")
#wmlp = WMLParser("../input/TA18-01_Xhosa_patterns_WML-form_pb_nopic.xml")
wmlp = WMLParser("/home/dustin/uni/bachelor-arbeit/data/fileserver/ocr-output/TA03_02_Xhosa_WML_formatted_pb_nopic_patterns.xml")

unknown = False 

parses = []

smallCapsStyles = [style for style, val in wmlp.extractStyleToSmallCaps().items() if val] 

for paragraph in wmlp.paragraphs:
	#lineParser = LineParser(paragraph.getText())

	lineParser = LineParserTa(paragraph.getText())

	smallCapsRanges = [rng for rng, style in paragraph.textRStyle.items() if style in smallCapsStyles]
	changed = True 
	while changed:
		changed = False
		for r1 in smallCapsRanges:
			for r2 in smallCapsRanges:
				if r1[1] == r2[0]:
					smallCapsRanges.append((r1[0],r2[1]))
					smallCapsRanges.remove(r1)
					smallCapsRanges.remove(r2)
					changed = True


	methods = [lineParser.matchConference, lineParser.matchMonograph, lineParser.matchArticle, lineParser.matchCollection]
	#curParse = lineParser.parseRecordLine(lineParser.rawStripped,[])
	for method in methods:
		curParse = None
		try:
			curParse = method(lineParser.rawStripped)
			if type(curParse) == type({}):
				curParse["type"] = method.__name__.replace("match", "").lower()
				break
		except:
			continue
from wordmlparser.wmlparser import WMLParser
from lineparsers.lineparser import LineParser

from lineparsers.lineparserta18 import LineParserTa

from alchemytransformer import transformToAlchemySyntax, getOffsets

#wmlp = WMLParser("../input/TA01_02_Xhosa_WML_formatted_pb_nopic_patterns.xml")
#wmlp = WMLParser("../input/TA18-01_Xhosa_patterns_WML-form_pb_nopic.xml")
wmlp = WMLParser("/home/dustin/uni/bachelor-arbeit/data/fileserver/ocr-output/TA03_02_Xhosa_WML_formatted_pb_nopic_patterns.xml")

unknown = False

parses = []

smallCapsStyles = [style for style, val in wmlp.extractStyleToSmallCaps().items() if val]

for paragraph in wmlp.paragraphs:
	#lineParser = LineParser(paragraph.getText())

	lineParser = LineParserTa(paragraph.getText())

	smallCapsRanges = [rng for rng, style in paragraph.textRStyle.items() if style in smallCapsStyles]
	changed = True
	while changed:
		changed = False
		for r1 in smallCapsRa
"""
"""from wordmlparser.wmlparser import WMLParser
from lineparsers.lineparser import LineParser

from lineparsers.lineparserta18 import LineParserTa

from alchemytransformer import transformToAlchemySyntax, getOffsets

#wmlp = WMLParser("../input/TA01_02_Xhosa_WML_formatted_pb_nopic_patterns.xml")
#wmlp = WMLParser("../input/TA18-01_Xhosa_patterns_WML-form_pb_nopic.xml")
wmlp = WMLParser("/home/dustin/uni/bachelor-arbeit/data/fileserver/ocr-output/TA03_02_Xhosa_WML_formatted_pb_nopic_patterns.xml")

unknown = False 

parses = []

smallCapsStyles = [style for style, val in wmlp.extractStyleToSmallCaps().items() if val] 

for paragraph in wmlp.paragraphs:
	#lineParser = LineParser(paragraph.getText())

	lineParser = LineParserTa(paragraph.getText())

	smallCapsRanges = [rng for rng, style in paragraph.textRStyle.items() if style in smallCapsStyles]
	changed = True 
	while changed:
		changed = False
		for r1 in smallCapsRanges:
			for r2 in smallCapsRanges:
				if r1[1] == r2[0]:
					smallCapsRanges.append((r1[0],r2[1]))
					smallCapsRanges.remove(r1)
					smallCapsRanges.remove(r2)
					changed = True


	methods = [lineParser.matchConference, lineParser.matchMonograph, lineParser.matchArticle, lineParser.matchCollection]
	#curParse = lineParser.parseRecordLine(lineParser.rawStripped,[])
	for method in methods:
nges:
			for r2 in smallCapsRanges:
				if r1[1] == r2[0]:
					smallCapsRanges.append((r1[0],r2[1]))
					smallCapsRanges.remove(r1)
					smallCapsRanges.remove(r2)
					changed = True


	methods = [lineParser.matchConference, lineParser.matchMonograph, lineParser.matchArticle, lineParser.matchCollection]
	#curParse = lineParser.parseRecordLine(lineParser.rawStripped,[])
	for method in methods:


	if unknown:
		if type(curParse) == type({}):
			pass
		else:#XXX
			curParse = lineParser.matchAnyRecord(lineParser.rawStripped)
			if type(curParse) == type({}):
				parses.append((curParse,smallCapsRanges))
	else:
		#if type(curParse) == type({}):
		if type(curParse) == type({}) and curParse["type"] == "article":
			parses.append((curParse,smallCapsRanges))
		
offsetParses = []


for parse,smallCapsRanges in parses:

	offsets = getOffsets(parse)
	offsets["raw"] = parse["raw"]
	offsetParses.append((offsets, smallCapsRanges))
del parses


atoms = transformToAlchemySyntax(offsetParses)
print("\n".join(atoms))
"""
