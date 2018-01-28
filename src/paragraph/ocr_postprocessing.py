# -*- coding: utf-8 -*-

import regex as re

broken_bullet_pattern = re.compile('^[φ#0]\s+', re.UNICODE)

def postprocess_paragraph(paragraph):
    text = paragraph['text']
    if broken_bullet_pattern.match(text):
        paragraph['original_text'] = text
        paragraph['text'] = '•' + text[1:]
    return paragraph
