import argparse
import csv
import logging
import pymongo
import os

import mongo_client
import parse_wml


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--import', dest='import_paragraphs', action='store_true', default=False, help='Import paragraphs from OCR')
    parser.add_argument('--ocr-dir', default='/home/dustin/work/ta/data/ocr', help='Location of OCR directory')
    parser.add_argument('--types', action='store_true', help='Determine entry types')
    parser.add_argument('--category-file', default='/home/dustin/work/ta/data/TA_Kategorien_Endschema.csv', help='Path to category CSV')


    args = parser.parse_args()

    database = mongo_client.get_database('ta')
    if args.import_paragraphs:
        write_paragraphs_to_database(args.ocr_dir, database)
    if args.types:
        category_mapping = get_category_mapping(args.category_file)
        determine_entry_types(database, category_mapping)


def get_category_mapping(file_name):
    with open(file_name, encoding='utf-8') as category_file:
        reader = csv.reader(category_file, delimiter=';')
        category_mapping = dict(reader)
        return category_mapping


def determine_entry_types(database, category_mapping):
    logging.info('Determining entry types...')
    for volume in database.paragraphs.distinct('volume'):
        volume_paragraphs = database.paragraphs.find({'volume': volume}).sort([('volume', pymongo.ASCENDING), ('index', pymongo.ASCENDING)])
        type_mapping = parse_wml.determine_entry_types(volume_paragraphs, category_mapping)
        for paragraph_id, paragraph_type in type_mapping.items():
            database.paragraphs.update_one({'_id': paragraph_id}, {'$set': {'type': paragraph_type}})
    database.paragraphs.create_index([('type', 1)])


def write_paragraphs_to_database(ocr_input_folder, database, drop_existing=True):
    if drop_existing:
        database.paragraphs.drop()
    volume_filenames = [os.path.join(ocr_input_folder, fileName) for fileName in os.listdir(ocr_input_folder) if
                        not fileName.startswith(".") and fileName.endswith(".xml")]
    volume_filenames.sort()
    for volume_filename in volume_filenames[:3]: # XXX limit for testing
        print("Processing %s..." % volume_filename)
        paragraphs = parse_wml.parse_volume_file(volume_filename)
        database.paragraphs.insert_many(list(paragraphs))
    database.paragraphs.create_index([('volume', 1)])


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
