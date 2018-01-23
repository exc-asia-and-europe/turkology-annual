# -*- coding: utf-8 -*-

import regex as re

from wordmlparser.wmlparser import WMLParser


def parse_volume_file(fileName):
    volume_number = fileName.split("/")[-1].split("_")[0][2:]
    if volume_number.isdigit():
        volume_number = int(volume_number)

    parser = WMLParser(fileName)
    paragraph_index = 0
    page_number_pattern = re.compile('(\d+\s+Turkologischer Anzeiger|Turkologischer Anzeiger\s+\d+){e<=2}')
    for raw_paragraph in parser.paragraphs:
        if not raw_paragraph.textRaw or (page_number_pattern.fullmatch(raw_paragraph.textRaw) and raw_paragraph.parId <= 1):  # and raw_paragraph.parId == 0:
            continue
        paragraph = parse_paragraph(raw_paragraph)
        paragraph['volume'] = volume_number
        paragraph['index'] = paragraph_index
        yield paragraph
        paragraph_index += 1


def determine_entry_types(paragraphs, category_mapping):
    category_pattern_base = '({})'.format(
        '|'.join([
            re.escape('{}. {}'.format(code, category))
            for code, category in category_mapping.items()
        ])
    )
    category_pattern_exact = re.compile(category_pattern_base, re.IGNORECASE)
    category_pattern_fuzzy = re.compile(category_pattern_base + '{e<=2}', re.IGNORECASE)
    entry_pattern = re.compile(r'(\d+)\.\s+.+')
    broken_bullet_pattern = re.compile(r'^[φ#].*, s\.( a\.)? \d+')

    category_seen = False
    latest_entry_number = 0
    previous_type = None
    type_mapping = {}


    for paragraph in paragraphs:
        paragraph_type = None
        text = paragraph['text']
        append_type_possible = previous_type == 'entry' or (previous_type and previous_type.startswith('append-'))
        entry_match = entry_pattern.fullmatch(text)
        if category_pattern_exact.fullmatch(text):
            paragraph_type = 'category'
        elif category_seen and entry_match and int(entry_match.group(1)) > latest_entry_number:
            paragraph_type = 'entry'
            latest_entry_number = int(entry_match.group(1))
        elif category_pattern_fuzzy.fullmatch(text):
            paragraph_type = 'category'
        elif category_seen and text.split('.')[0] in category_mapping:
            paragraph_type = 'category'
        elif text.startswith('•') and append_type_possible:
            paragraph_type = 'append-bullet'
        elif text.startswith('Rez.') and append_type_possible:
            paragraph_type = 'append-review'
        elif text.startswith('Bericht') and append_type_possible:
            paragraph_type = 'append-report'
        elif text == 'Autoren, Herausgeber, Übersetzer, Rezensenten' or text == 'INDEX':
            paragraph_type = 'author-index-begin'
        elif broken_bullet_pattern.match(text) and append_type_possible:
            paragraph_type = 'append-bullet-fuzzy'

        if paragraph_type == 'category':
            category_seen = True

        if not 'type' in paragraph or paragraph.get('type') != paragraph_type:
            type_mapping[paragraph['_id']] = paragraph_type
        previous_type = paragraph_type
    return type_mapping


def parse_paragraph(wmlParagraph):
    result = {
        'id': wmlParagraph.parId,
        #'tblId': wmlParagraph.tblId,
        'text': wmlParagraph.textRaw if wmlParagraph.textRaw else '',
    }

    '''smallCapsStyles = [style for style, val in wmlParagraph.parser.extractStyleToSmallCaps().items() if val]
    ranges = sorted(join_character_ranges([rng for rng, style in wmlParagraph.textRStyle.items() if style in smallCapsStyles]))
    result['smallCapsRanges'] = [
        {
            'start': rng[0],
            'end': rng[1],
        } for rng in ranges
    ]'''
    return result


def join_character_ranges(ranges):
    """Vereint benachbarte Character Ranges des gleichen Typs"""
    changed = True
    while changed:
        changed = False
        for r1 in ranges:
            for r2 in ranges:
                if r1[1] == r2[0]:
                    ranges.append((r1[0], r2[1]))
                    ranges.remove(r1)
                    ranges.remove(r2)
                    changed = True
    return ranges
