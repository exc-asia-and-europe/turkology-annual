# -*- coding: utf-8 -*-

import logging
import re
import regex

from .field_parsing import parse_citation_fields


class CitationParser(object):
    given_names_pattern = '(?:\w{1,2}\.(?:-\w{1,2}\.)?|[\w-]+)(?: (?:\w{1,2}\.(?:-\w{1,2}\.)?|[\w-]+))*'
    last_name_pattern = '\*?(?:\w+ ){,2}[\w\'-]+'

    last_name_given_names_pattern = '(?:{}, +{})'.format(last_name_pattern, given_names_pattern)
    given_names_last_name_pattern = '(?:{} +{})'.format(given_names_pattern, last_name_pattern)

    number_rest_pattern = re.compile('(\d+)\.\s*(.+)', re.DOTALL)
    review_pattern = re.compile(' +(Rez\.|Abstract +in:) (.*)$')
    comment_pattern = re.compile('\[([^\]]+)\]\.?( {{{ REVIEW }}})?$')
    material_pattern = re.compile(', (\[?\d+\]? *(?:(?:Karte|Tafel|Tabelle|Falt(?:tafel|karte|tabelle))n?|Porträts?|Abb\.(?:Falt|Schlacht)pl(?:an|äne)))(\.)?')
    loc_year_pages_pattern = re.compile(r'([.,]) +\[?([^,.]+), +\[?(\d{4})\]?, +(?:([\d +DCLIVX]+) *[Ss]\.|[Ss]\. (\d+)\s*-\s*(\d+))')
    in_pattern = re.compile(' +In ?: +([^.]+ +[\d.\-— ();,*S/=und]+)[.,]')
    author_pattern = re.compile('^{last_given}   +'.format(last_given=last_name_given_names_pattern), re.UNICODE)
    multiple_authors_pattern = re.compile(
        '^{last_given}(?: *[—-] *{last_given})+   +'.format(last_given=last_name_given_names_pattern), re.UNICODE)
    role_person_pattern = re.compile('\. *({given_last}) (ed|trs)\.'.format(given_last=given_names_last_name_pattern))
    role_persons_pattern = re.compile(
        '\. ({given_last}(?: *— *{given_last})+) (ed|trs)\.'.format(given_last=given_names_last_name_pattern))
    title_patterns = [
        re.compile('{{{ AUTHOR }}}\s*(.+)\s*{{{ IN }}}'),
        re.compile('{{{ AUTHOR }}}\s*(.+)\s*{{{ PERSON }}}'),
        re.compile('{{{ AUTHOR }}}\s*([^.(]+?)[.,]?\s*{{{'),
    ]
    weird_parentheses_pattern = re.compile('{{{ (?:PAGE_NUM|MATERIAL) }}}([ .,]*\(([^)]+)\)\.?)')

    fully_parsed_pattern = re.compile('({{{\s*[\w_]+\s*}}}[., ]*)+')

    @classmethod
    def parse_citation(cls, citation):
        logging.debug('Parsing citation: {}'.format(str(citation)))
        if 'remainingText' in citation:
            remaining_text = citation['remainingText']
        else:
            citation_number, remaining_text = cls.number_rest_pattern.match(citation['rawText']).groups()
            citation['number'] = int(citation_number)

        review_match = cls.review_pattern.search(remaining_text)
        if review_match:
            review_type = review_match.group(1)
            if review_type == 'Rez.':
                citation['reviews'] = [review_match.group(2)]
            elif re.sub(' {2,}', ' ', review_type).lower() == 'abstract in:':
                citation['abstractIn'] = review_match.group(2)
            remaining_text = remaining_text[:review_match.span()[0]] + ' {{{ REVIEW }}}'

        comment_match = cls.comment_pattern.search(remaining_text)
        if comment_match:
            citation['comment'] = comment_match.group(1).strip().rstrip('.')
            remaining_text = remaining_text[:comment_match.span()[0]] + ' {{{ COMMENT }}}'
            if comment_match.group(2):
                remaining_text += comment_match.group(2)

        material_spans = []
        for material_match in re.finditer(cls.material_pattern, remaining_text):
            citation.setdefault('material', []).append(material_match.group(1))
            material_spans.append((material_match.span(1)[0], material_match.span()[1]))

        if material_spans:
            remaining_text_parts = []
            previous_end = 0
            for start, end in material_spans:
                remaining_text_parts.append(remaining_text[previous_end:start])
                remaining_text_parts.append('{{{ MATERIAL }}}')
                previous_end = end
            remaining_text_parts.append(remaining_text[previous_end:])
            remaining_text = ''.join(remaining_text_parts)

        loc_year_pages_match = cls.loc_year_pages_pattern.search(remaining_text)
        if loc_year_pages_match:
            citation['location'] = loc_year_pages_match.group(2).strip()
            citation['datePublished'] = int(loc_year_pages_match.group(3))
            if loc_year_pages_match.group(4):
                number_of_pages = loc_year_pages_match.group(4).strip()
                citation['numberOfPages'] = int(number_of_pages) if number_of_pages.isdigit() else number_of_pages
            else:
                citation['pageStart'] = int(loc_year_pages_match.group(5))
                citation['pageEnd'] = int(loc_year_pages_match.group(6))
            remaining_text = remaining_text[:loc_year_pages_match.span()[0]] + loc_year_pages_match.group(1) + ' {{{ LOCATION }}} {{{ YEAR }}} {{{ PAGE_NUM }}}' + remaining_text[loc_year_pages_match.span()[1]:]

        weird_parentheses_match = cls.weird_parentheses_pattern.search(remaining_text)
        if weird_parentheses_match:
            citation['weirdParentheses'] = weird_parentheses_match.group(2).strip()  # TODO: Find out what this field is
            remaining_text = remaining_text[:weird_parentheses_match.span(1)[0]] + remaining_text[weird_parentheses_match.span(1)[1]:]

        in_match = cls.in_pattern.search(remaining_text)
        if in_match:
            citation['in'] = in_match.group(1)
            remaining_text = remaining_text[:in_match.span()[0]] + ' {{{ IN }}}' + remaining_text[in_match.span()[1]:]

        multiple_authors_match = cls.multiple_authors_pattern.search(remaining_text)
        if multiple_authors_match:
            citation['authors'] = [author.strip() for author in multiple_authors_match.group().split('—')]
            remaining_text = '{{{ AUTHOR }}} ' + remaining_text[multiple_authors_match.span()[1]:].strip()

        author_match = cls.author_pattern.search(remaining_text)
        if author_match:
            citation['authors'] = [author_match.group().strip()]
            remaining_text = '{{{ AUTHOR }}} ' + remaining_text[author_match.span()[1]:].strip()

        role_person_match = cls.role_person_pattern.search(remaining_text)
        if role_person_match:
            role_name = {'ed': 'editors', 'trs': 'translators'}[role_person_match.group(2)]
            citation[role_name] = [role_person_match.group(1)]
            remaining_text = remaining_text[:role_person_match.span(1)[0]] + ' {{{ PERSON }}} ' + remaining_text[role_person_match.span()[1]:]

        multiple_role_persons_match = cls.role_persons_pattern.search(remaining_text)
        if multiple_role_persons_match:
            role_name = {'ed': 'editors', 'trs': 'translators'}[multiple_role_persons_match.group(2)]
            citation[role_name] = multiple_role_persons_match.group(1).strip().split('—')
            remaining_text = remaining_text[:multiple_role_persons_match.span(1)[0]] + ' {{{ PERSON }}} ' + remaining_text[
                                                                                             multiple_role_persons_match.span()[1]:]

        for title_pattern in cls.title_patterns:
            title_match = title_pattern.search(remaining_text)
            if title_match:
                citation['title'] = title_match.group(1).strip().rstrip('.,')
                remaining_text = remaining_text[:title_match.span(1)[0]] + '{{{ TITLE }}}' + remaining_text[title_match.span(1)[1]:]
                break

        citation['remainingText'] = remaining_text
        if cls.fully_parsed_pattern.fullmatch(remaining_text):
            citation['fullyParsed'] = True
        else:
            citation['fullyParsed'] = False
        return parse_citation_fields(citation)
        #return citation


    def find_known_authors(self, citations, known_authors):
        authors_pattern = regex.compile('^({})\.?\s+(\p{{Lu}}[^ .] )'.format('|'.join([re.escape(author) for author in known_authors])))
        for citation in citations:
            author_match = authors_pattern.search(citation['remainingText'])
            if author_match:
                author_name = author_match.group(1)
                remaining_text = '{{{ AUTHOR }}} ' + citation['remainingText'][author_match.span(2)[0]:]
                citation['remainingText'] = remaining_text
                if self.fully_parsed_pattern.fullmatch(remaining_text):
                    citation['fullyParsed'] = True
                citation['authors'] = [author_name]
                yield citation



if __name__ == '__main__':
    from pprint import pprint
    parser = CitationParser()
    for text in [
        '337. Özkirimli, Atillâ   Nedim. [Istanbul, 1974],  175 S. [Der Dichter Nedīm, ca. 1681-1730.]',
        "301. Yotjnous, Emre   Poèmes. Guzine Dino—Marc Delouze trs. Paris, 1973, 41 S.",
        "863. Nye, Roger P.   The military in Turkish politics, 1960-1973. Diss., Washington University, 1974, 302 S. (UM 74-22,540). Abstract in: DAI 35.4.1974-1975.2358-A.",
        "222. Süleyman the Magnificent and his age [s.TA 22 - 23.293]. Rez. György domokos, 110.4.1997.814.",
        "9. Dërfer, G.    0 sostojanii tjurkologii v Federativnoj Respublike Germanii. In: ST 1974.6.98-109. [Die Turkologie in der Bundesrepublik Deutschland.]",
        "1272. DEVECI, Hasan A.    Cyprus yesterday, today — what next? London, 1976, 1 + 60 S. (Cyprus Turkish Association, 2).",
        "660. Kramer, Gerhard F.—McGrew, Roderick E.  Potemkin, the Porte, and the road to Tsargrad. The Shumla negotiations, 1789-1790. In: CASS 8.4.1974.467-487.",
        "1226. Pollo, St. - Pulaha, S.     Akte të Rilindjes kombëtare shqiptare 1878-1912 [s. TA 5.1496, 6.1621].",
        '1018. PlNON, Pierre       Les villes du pont vues par le Père de Jerphanion.      e g Tokat, Amasya, Sivas. In: TA 25.240.859-865.                                      CO Ό',
    ]:
        # TA 2.162.3.1.1973.29-36

        pprint(parser.parse_citation({'volume': None, 'rawText': text}))
