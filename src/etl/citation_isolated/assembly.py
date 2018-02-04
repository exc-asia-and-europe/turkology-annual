# -*- coding: utf-8 -*-

from collections import OrderedDict


def assemble_citations(paragraphs):
    current_category = None
    current_citation = None

    for paragraph in paragraphs:
        if paragraph['type'] == 'category':
            current_category = paragraph['text']
        elif paragraph['type'] == 'citation':
            if current_citation:
                yield current_citation
            current_citation = OrderedDict(
                volume=paragraph['volume'],
                category=current_category,
                rawText=paragraph['text'],
            )
            if 'small_caps_ranges' in paragraph:
                current_citation['small_caps_ranges'] = paragraph['small_caps_ranges']
        elif paragraph['type'] and paragraph['type'] == 'amendment':
            current_citation.setdefault('amendments', []).append(paragraph['text'])
    if current_citation:
        yield current_citation
