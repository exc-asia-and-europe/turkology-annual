# -*- coding: utf-8 -*-

from collections import OrderedDict
from datetime import datetime


def assemble_citations(paragraphs):
    current_keyword = None
    current_citation = None

    for paragraph in paragraphs:
        if paragraph['type'] == 'keyword':
            current_keyword = paragraph['text']
        elif paragraph['type'] == 'citation':
            if current_citation:
                yield current_citation
            current_citation = OrderedDict(
                volume=paragraph['volume'],
                keywords=[current_keyword],
                rawText=paragraph['text'],
                _version=1,
                _timestamp=datetime.now(),
                _creator='<initial>',
            )
            if 'small_caps_ranges' in paragraph:
                current_citation['small_caps_ranges'] = paragraph['small_caps_ranges']
        elif paragraph['type'] and paragraph['type'] == 'amendment':
            current_citation.setdefault('amendments', []).append(paragraph['text'])
    if current_citation:
        yield current_citation
