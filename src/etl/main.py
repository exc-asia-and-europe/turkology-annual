import argparse
import csv
import logging
import multiprocessing

from repositories.MongoRepository import MongoRepository
from etl.paragraph.paragraph_extraction import extract_paragraphs
from etl.paragraph.type_detection import detect_paragraph_types
from etl.citation_isolated.assembly import assemble_citations
from etl.citation_isolated.citation_parsing import CitationParser


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--full', action='store_true', help='Run full pipeline')
    parser.add_argument('--ocr-files', default='../../data/ocr/TA*.xml', nargs='*', help='Location of OCR directory')
    parser.add_argument('--category-file', default='../../data/TA_Kategorien_Endschema.csv',
                        help='Path to category CSV')
    parser.add_argument('--find-authors', action='store_true')
    parser.add_argument('--verbose', '-v', action='store_true')

    args = parser.parse_args()

    setup_logging(args.verbose)

    repository = MongoRepository('ta')
    if args.full:
        run_full_pipeline(args.ocr_files, args.category_file, repository)
        return

    if args.find_authors:
        known_authors = set([author.strip() for author in repository.citations.distinct('authors') if author])
        citations = repository.citations.find({'authors': None, 'fullyParsed': False})
        parser = CitationParser()
        for count, citation in enumerate(parser.find_known_authors(citations, known_authors)):
            if citation.get('authors'):
                citation = parser.parse_citation(citation)
                repository.citations.save(citation)
        logging.info('Found known authors in %d citations', count+1)


def run_full_pipeline(ocr_files, category_file, repository, drop_existing=True):
    category_mapping = get_category_mapping(category_file)
    if drop_existing:
        repository.drop_database()

    with multiprocessing.Pool() as pool:
        pool.starmap(run_full_pipeline_on_volume, [(volume_filename, category_mapping) for volume_filename in ocr_files])


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
    repository = MongoRepository('ta')

    logging.debug('Writing paragraphs to database...')
    repository.insert_paragraphs(typed_paragraphs)

    logging.debug('Assembling citations...')
    raw_citations = assemble_citations(typed_paragraphs)

    logging.debug('Parsing citations...')
    citations = [parser.parse_citation(raw_citation) for raw_citation in raw_citations]

    if citations:
        logging.debug('Writing {} citations to database...'.format(len(citations)))

        repository.insert_citations(citations)
    else:
        logging.warning('No citations found.')
    logging.info('Processing of %s done.', volume_filename)


def get_category_mapping(file_name):
    with open(file_name, encoding='utf-8') as category_file:
        reader = csv.reader(category_file, delimiter=';')
        category_mapping = dict(reader)
        return category_mapping


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
