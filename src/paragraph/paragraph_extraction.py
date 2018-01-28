# -*- coding: utf-8 -*-

from paragraph.wmlparser import WMLParser


def extract_paragraphs(volume_filename):
    volume_number = volume_filename.split("/")[-1].split("_")[0][2:]
    if volume_number.isdigit():
        volume_number = int(volume_number)

    parser = WMLParser(volume_filename)
    paragraph_index = 0
    for raw_paragraph in parser.paragraphs:
        paragraph = parse_paragraph(raw_paragraph)
        paragraph['volume'] = volume_number
        paragraph['index'] = paragraph_index
        yield paragraph
        paragraph_index += 1


def parse_paragraph(wmlParagraph):
    result = {
        'id': wmlParagraph.parId,
        #'tblId': wmlParagraph.tblId,
        'text': wmlParagraph.textRaw.replace(u"\u00A0", " ") if wmlParagraph.textRaw else '',
    }
    if wmlParagraph.parser:
        smallCapsStyles = [style for style, val in wmlParagraph.parser.extractStyleToSmallCaps().items() if val]
        ranges = sorted(join_character_ranges([rng for rng, style in wmlParagraph.textRStyle.items() if style in smallCapsStyles]))
        if ranges:
            result['small_caps_ranges'] = ranges
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
