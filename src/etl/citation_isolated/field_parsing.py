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
    }.get(field_name, lambda x:x)

    if isinstance(value, list):
        return [parse_function(sub_value) or sub_value for sub_value in value]
    else:
        return parse_function(value) or value


def parse_name(name):
    return nameparser.HumanName(name).as_dict(include_empty=False)


ta_reference_pattern = re.compile('^TA *(?P<volume>\d+)\.(?P<entry_number>\d+)\.(?P<page_start>\d+)-(?P<page_end>\d+)$')

def parse_reference(reference):
    ta_reference_match = ta_reference_pattern.search(reference)
    if ta_reference_match:
        group_dict = ta_reference_match.groupdict()
        for key, value in list(group_dict.items())[:]:
            group_dict[key] = int(value)
        group_dict['type'] = 'ta'
        return group_dict

