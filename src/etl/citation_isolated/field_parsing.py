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
    }.get(field_name, lambda x:x)

    if isinstance(value, list):
        return [parse_function(sub_value) or sub_value for sub_value in value]
    else:
        return parse_function(value) or value


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
