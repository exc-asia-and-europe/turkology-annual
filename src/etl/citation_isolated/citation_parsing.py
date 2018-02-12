# -*- coding: utf-8 -*-

import logging
import re
import regex

try:
    from .field_parsing import parse_citation_fields
except:
    from field_parsing import parse_citation_fields


class CitationParser(object):
    given_names_pattern = '(?:\w{1,2}\.(?:-\w{1,2}\.)?|[\w-]+)(?: (?:\w{1,2}\.(?:-\w{1,2}\.)?|[\w-]+)){,3}'
    last_name_pattern = '\*?(?:\w+ ){,2}[\w\'-]+'

    last_name_given_names_pattern = '(?:{}, +{})'.format(last_name_pattern, given_names_pattern)
    given_names_last_name_pattern = '(?:{} +{})'.format(given_names_pattern, last_name_pattern)

    number_rest_pattern = re.compile('(\d+)\.\s*(.+)', re.DOTALL)
    review_pattern = re.compile(' +(Rez\.|Abstract +in:) (.*)$')
    comment_pattern = re.compile('\[([^\]]+)\]\.?( {{{ REVIEW }}})?$')
    material_pattern = re.compile(
        ', (\[?\d+\]? *(?:(?:Karte|Tafel|Tabelle|Falt(?:tafel|karte|tabelle))n?|Porträts?|Abb\.|Tab\.|(?:Falt|Schlacht)pl(?:an|äne)))(\.)?')
    loc_year_pages_pattern = re.compile(
        r'([.,]) +\[?([^,.]+), *\[?(\d{4})\]?, *(?:([\d +DCLIVX]+) *[Ss]\.|[Ss]\. (\d+)\s*[-—]\s*(\d+))')
    loc_date_pattern = re.compile(
        '^([^,]+), *((?:\d{1,2}\. *(?:(?:[IVX]{1,4})\. *)?(?:\d{4})?[-—])?\d{1,2}\. *[IVX]{1,4}\. *\d{4})'
    )
    in_pattern = re.compile(' +In ?: +([^.]+ +[\d.\-— ();,*S/=und]+)[.,]')
    author_pattern = re.compile('^({last_given})   +'.format(last_given=last_name_given_names_pattern), re.UNICODE)
    author_pattern_volume_1 = re.compile('^(%s\.):?(?<!geb\.) (?!{{{)+' % last_name_given_names_pattern, re.UNICODE)
    multiple_authors_pattern = re.compile(
        '^{last_given}(?: *([—-]) *{last_given})+   +'.format(last_given=last_name_given_names_pattern), re.UNICODE)
    role_person_pattern = re.compile('\. *({given_last}) (ed|trs)\.'.format(given_last=given_names_last_name_pattern))
    role_persons_pattern = re.compile(
        '\. ({given_last}(?: *(—| und ) *{given_last})+) (ed|trs)\.'.format(given_last=given_names_last_name_pattern))
    title_patterns = [
        re.compile('{{{ AUTHOR }}}\s*(.+)\s*{{{ IN }}}'),
        re.compile('{{{ AUTHOR }}}\s*(.+)\s*{{{ PERSON }}}'),
        re.compile('{{{ AUTHOR }}}\s*([^.(]+?)[.,]?\s*{{{'),
        re.compile('^([^.,(]+?)[.,]?\s*{{{ (?:IN|PERSON) '),
    ]
    weird_parentheses_pattern = re.compile('{{{ (?:PAGE_NUM|MATERIAL) }}}([ .,]*\(([^)]+)\)\.?)')

    fully_parsed_pattern = re.compile('({{{\s*[\w_]+\s*}}}[., ]*)+')

    @classmethod
    def parse_citation(cls, citation):
        logging.debug('Parsing citation: {}'.format(str(citation)))
        if 'remainingText' in citation:
            text = citation['remainingText']
        else:
            citation_number, text = cls.number_rest_pattern.match(citation['rawText']).groups()
            citation['number'] = int(citation_number)

        review_match = cls.review_pattern.search(text)
        if review_match:
            review_type = review_match.group(1)
            if review_type == 'Rez.':
                citation['reviews'] = [review_match.group(2)]
            elif re.sub(' {2,}', ' ', review_type).lower() == 'abstract in:':
                citation['abstractIn'] = review_match.group(2)
            text = text[:review_match.span()[0]] + ' {{{ REVIEW }}}'

        comment_match = cls.comment_pattern.search(text)
        if comment_match:
            citation['comment'] = comment_match.group(1).strip().rstrip('.')
            text = text[:comment_match.span()[0]] + ' {{{ COMMENT }}}'
            if comment_match.group(2):
                text += comment_match.group(2)

        match = cls.loc_date_pattern.search(text)
        if match:
            citation['location'] = match.group(1)
            citation['date'] = match.group(2)
            citation['type'] = 'conference'
            text = '{{{ LOCATION }}} {{{ DATE }}} ' + text[match.span()[1]:]


        material_spans = []
        for material_match in re.finditer(cls.material_pattern, text):
            citation.setdefault('material', []).append(material_match.group(1))
            material_spans.append((material_match.span(1)[0], material_match.span()[1]))

        if material_spans:
            remaining_text_parts = []
            previous_end = 0
            for start, end in material_spans:
                remaining_text_parts.append(text[previous_end:start])
                remaining_text_parts.append('{{{ MATERIAL }}}')
                previous_end = end
            remaining_text_parts.append(text[previous_end:])
            text = ''.join(remaining_text_parts)

        loc_year_pages_match = cls.loc_year_pages_pattern.search(text)
        if loc_year_pages_match:
            citation['location'] = loc_year_pages_match.group(2).strip()
            citation['datePublished'] = int(loc_year_pages_match.group(3))
            if loc_year_pages_match.group(4):
                number_of_pages = loc_year_pages_match.group(4).strip()
                citation['numberOfPages'] = int(number_of_pages) if number_of_pages.isdigit() else number_of_pages
            else:
                citation['pageStart'] = int(loc_year_pages_match.group(5))
                citation['pageEnd'] = int(loc_year_pages_match.group(6))
            text = text[:loc_year_pages_match.span()[0]] + loc_year_pages_match.group(
                1) + ' {{{ LOCATION }}} {{{ YEAR }}} {{{ PAGE_NUM }}}' + text[loc_year_pages_match.span()[1]:]

        weird_parentheses_match = cls.weird_parentheses_pattern.search(text)
        if weird_parentheses_match:
            citation['weirdParentheses'] = weird_parentheses_match.group(2).strip()  # TODO: Find out what this field is
            text = text[:weird_parentheses_match.span(1)[0]] + text[
                                                                                   weird_parentheses_match.span(1)[1]:]

        in_match = cls.in_pattern.search(text)
        if in_match:
            citation['in'] = in_match.group(1)
            citation['type'] = 'article'
            text = text[:in_match.span()[0]] + ' {{{ IN }}}' + text[in_match.span()[1]:]

        multiple_authors_match = cls.multiple_authors_pattern.search(text)
        if multiple_authors_match:
            citation['authors'] = [author.strip() for author in
                                   multiple_authors_match.group().split(multiple_authors_match.group(1))]
            text = '{{{ AUTHOR }}} ' + text[multiple_authors_match.span()[1]:].strip()

        if citation['volume'] == 1:
            author_match = cls.author_pattern_volume_1.search(text)
        else:
            author_match = cls.author_pattern.search(text)
        if author_match:
            citation['authors'] = [author_match.group(1).strip()]
            text = '{{{ AUTHOR }}} ' + text[author_match.span()[1]:].strip()

        multiple_role_persons_match = cls.role_persons_pattern.search(text)
        if multiple_role_persons_match:
            role_name = {'ed': 'editors', 'trs': 'translators'}[multiple_role_persons_match.group(3)]
            citation[role_name] = multiple_role_persons_match.group(1).strip().split(
                multiple_role_persons_match.group(2))
            text = text[:multiple_role_persons_match.span(1)[0]] + ' {{{ PERSON }}} ' + text[
                                                                                             multiple_role_persons_match.span()[
                                                                                                 1]:]
        role_person_match = cls.role_person_pattern.search(text)
        if role_person_match:
            role_name = {'ed': 'editors', 'trs': 'translators'}[role_person_match.group(2)]
            citation[role_name] = [role_person_match.group(1)]
            text = text[:role_person_match.span(1)[0]] + ' {{{ PERSON }}} ' + text[role_person_match.span()[1]:]

        if citation.get('editors'):
            citation['type'] = 'collection'

        for title_pattern in cls.title_patterns:
            title_match = title_pattern.search(text)
            if title_match:
                citation['title'] = title_match.group(1).strip().rstrip('.,')
                text = text[:title_match.span(1)[0]] + '{{{ TITLE }}}' + text[title_match.span(1)[1]:]
                break

        citation['remainingText'] = text
        if cls.fully_parsed_pattern.fullmatch(text):
            citation['fullyParsed'] = True
        else:
            citation['fullyParsed'] = False
        return parse_citation_fields(citation)

    def find_known_authors(self, citations, known_authors):
        known_authors = '|'.join([re.escape(author) for author in known_authors])
        authors_pattern = regex.compile('^({}){{e<=1}}\.?\s+(\p{{Lu}}[^ .]+ )'.format(known_authors),
                                        regex.UNICODE | regex.IGNORECASE)
        multiple_authors_pattern = regex.compile(
            '^({}){{e<=1}}(?: *[—-] *({}){{e<=1}})+\.?\s+(\p{{Lu}}[^ .]+ .+)'.format(known_authors, known_authors),
            regex.UNICODE | regex.IGNORECASE | regex.DOTALL)

        for citation in citations:
            authors_match = multiple_authors_pattern.findall(citation['remainingText'])
            if authors_match:
                authors_match = authors_match[0]
                author_names = [name.strip() for name in authors_match[:-1]]
                remaining_text = '{{{ AUTHOR }}} ' + authors_match[-1]
                citation['remaingText'] = remaining_text
                citation['authors'] = author_names
                yield citation
                continue
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
        '3. Biographisches Lexikon zur Geschichte Südosteuropas. Mathias Bernath und Felix v. Schroeder ed., Gerda Bartl (Red.). Bd. 1, Α-F. München, 1974, XV+557 S. (Südosteuropäische Arbeiten, 75). Rez. Gerhard Stadler, Donauraum 19.3.-4.1974.209. — Johann Weidlein, SODV 23.3.1974.218.',
        '701. Brouček, Peter-LEiτscH, Walter-VocELKA, Karl—Wimmer, Jan-Wój-cıκ, Zbigniew Der Sieg bei Wien 1683. Wien-Warszawa, 1983, 187 S. 70 Abb., 4 Schlachtpläne, 1 Faltplan.',
        '117. Leningrad, 2.-4. VI. 1969: III Tjurkologičeskaja konferencija. 3. Turkologische Konferenz; die Referate sind abgedruckt in TA 1.89. Bericht: V.G.Guzev,N. A.Dulina,L. Ju.Tuguševa, TA 1.89.403-412.',
    ]:
        # TA 2.162.3.1.1973.29-36

        pprint(parser.parse_citation({'volume': None, 'rawText': text}))
