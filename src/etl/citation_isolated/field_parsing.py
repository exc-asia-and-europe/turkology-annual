from datetime import datetime
import logging
import nameparser
import re


def parse_citation_fields(citation):
    return {
        field: parse_field(field, value) for field, value in citation.items()
    }


def parse_field(field_name, value):
    parse_function = {
        'authors': parse_name,
        'editors': parse_name,
        'translators': parse_name,
        'in': parse_reference,
        'material': parse_material,
        'date': parse_date,
    }.get(field_name, lambda x: x)

    try:
        if isinstance(value, list):
            return [parse_function(sub_value) or sub_value for sub_value in value]
        else:
            return parse_function(value) or value
    except:
        logging.exception('Error parsing field \'{}\' with value \'{}\''.format(field_name, value))

def parse_name(name):
    if not isinstance(name, str):
        return name
    name_dict = nameparser.HumanName(name).as_dict(include_empty=False)
    name_dict['raw'] = name
    return name_dict


ta_reference_pattern = re.compile('^TA *(?P<volume>\d+)\.(?P<number>\d+)\.(?P<pageStart>\d+)[-—](?P<pageEnd>\d+)$')


def parse_reference(reference):
    if not isinstance(reference, str):
        return reference
    ta_reference_match = ta_reference_pattern.search(reference)
    if ta_reference_match:
        group_dict = ta_reference_match.groupdict()
        for key, value in list(group_dict.items())[:]:
            group_dict[key] = int(value)
        group_dict['type'] = 'ta'
        group_dict['raw'] = reference
        return group_dict


def parse_material(material):
    if not isinstance(material, str):
        return material
    match = re.match('(\d+) *(.+)', material)
    if not match:
        return material
    count = match.group(1)
    material_types = {
        '(?:Tab\.|Tabellen?|Tafeln?)': 'table',
        '(?:Karten?)': 'map',
        '(?:Falt(?:karten?|plan|pläne))': 'fold-up map',
        '(?:Falttabellen?)': 'fold-up table',
        '(?:Abb\.)': 'figure',
    }
    for type_pattern, type_name in material_types.items():
        if re.match(type_pattern, match.group(2)):
            break
        else:
            type_name = match.group(2)
    return {
        'count': int(count),
        'type': type_name,
        'raw': material,
    }


def parse_date(date_str):
    if not isinstance(date_str, str):
        return date_str

    match = re.match(
        '(?:(\d{1,2})\. *(?:([IVX]{1,4})\. *)?(\d{4})?[-—])?(\d{1,2})\. *([IVX]{1,4})\. *(\d{4})',
        date_str
    )

    if match:
        roman_numerals = ('i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii', 'viii', 'ix', 'x', 'xi', 'xii')
        day_end = int(match.group(4))
        month_end = roman_numerals.index(match.group(5).lower()) + 1
        year_end = int(match.group(6))

        day_start = int(match.group(1)) if match.group(1) else day_end
        month_start = roman_numerals.index(match.group(2).lower()) + 1 if match.group(2) else month_end
        year_start = int(match.group(3)) if match.group(3) else year_end

        date_start = datetime(year_start, month_start, day_start)
        date_end = datetime(year_end, month_end, day_end)

        return {
            'start': date_start,
            'end': date_end,
        }
