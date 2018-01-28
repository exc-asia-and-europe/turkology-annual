import regex as re


def detect_paragraph_types(paragraphs, category_mapping):
    category_pattern_base = '({})'.format(
        '|'.join([
            re.escape('{}. {}'.format(code, category))
            for code, category in category_mapping.items()
        ])
    )
    category_pattern_exact = re.compile(category_pattern_base, re.IGNORECASE)
    category_pattern_fuzzy = re.compile(category_pattern_base + '{e<=2}', re.IGNORECASE)
    citation_pattern = re.compile(r'(\d+)\.\s+.+')
    broken_bullet_pattern = re.compile(r'^[φ#0].*')#, s\.( a\.)? \d+')
    page_number_pattern = re.compile('(\d+\s+Turkologischer Anzeiger|Turkologischer Anzeiger\s+\d+){e<=2}')


    category_seen = False
    latest_citation_number = 0
    previous_type = None
    index_has_begun = False

    for paragraph in paragraphs:
        paragraph_type = None
        text = paragraph['text']
        is_possible_amendment = previous_type == 'citation' or (previous_type and previous_type == 'amendment')
        citation_match = citation_pattern.fullmatch(text)
        if not index_has_begun:
            if category_pattern_exact.fullmatch(text):
                paragraph_type = 'category'
            elif category_seen and citation_match and 0 < (int(citation_match.group(1)) - latest_citation_number) <= 5:
                paragraph_type = 'citation'
                latest_citation_number = int(citation_match.group(1))
            elif category_pattern_fuzzy.fullmatch(text):
                paragraph_type = 'category'
            elif category_seen and text.split('.')[0] in category_mapping:
                paragraph_type = 'category'
            elif text.startswith('•') and is_possible_amendment:
                paragraph_type = 'amendment'
            elif text.startswith('Rez.') and is_possible_amendment:
                paragraph_type = 'amendment'
            elif text.startswith('Bericht') and is_possible_amendment:
                paragraph_type = 'amendment'
            elif text == 'Autoren, Herausgeber, Übersetzer, Rezensenten' or text == 'INDEX':
                paragraph_type = 'author-index-begin'
                index_has_begun = True
            elif broken_bullet_pattern.match(text) and is_possible_amendment:
                paragraph_type = 'amendment'

        if paragraph_type == 'category':
            category_seen = True
        paragraph['type'] = paragraph_type
        yield paragraph
        if not page_number_pattern.fullmatch(text):
            previous_type = paragraph_type
