from collections import OrderedDict
from lxml import etree


class WMLParser(object):
    def __init__(self, xmlFileName):
        self.namespaces = {
            'w': 'http://schemas.microsoft.com/office/word/2003/wordml',
            'wx': 'http://schemas.microsoft.com/office/word/2003/auxHint',
        }
        self.document = self._parse_document(xmlFileName)
        self.styles = self._extract_char_styles()
        self.paragraphs = self._extract_paragraphs()

    def _parse_document(self, xml_filename):
        return etree.parse(xml_filename).getroot()


    ''' <wx:font wx:val="Arial Unicode MS"></wx:font>
      <w:sz w:val="16"></w:sz>
      <w:sz-cs w:val="16"></w:sz-cs>
      <w:b w:val="off"></w:b>
      <w:b-cs w:val="off"></w:b-cs>
      <w:i w:val="off"></w:i>
      <w:i-cs w:val="off"></w:i-cs>
      <w:smallCaps w:val="off"></w:smallCaps>'''

    def _extract_char_styles(self):
        char_styles = OrderedDict()
        for style_node in self._xpath('/w:styles/w:style[@w:type=\'character\']'):
            char_style = {}
            style_id = self._xpath('./@w:styleId', element=style_node)[0]
            for attribute_node in self._xpath('w:rPr/*[not(@w:val)]|w:rPr/*[@w:val!=\'off\']', element=style_node):
                value = attribute_node.get('{%s}%s' % (self.namespaces['wx'], 'val')) or attribute_node.get('{%s}%s' % (self.namespaces['w'], 'val'))
                if value:
                    if value == 'on':
                        value = True
                    elif value.isdigit():
                        value = int(value)
                else:
                    value = True
                attribute_name = attribute_node.tag.split('}')[1]
                char_style[attribute_name] = value
            char_styles[style_id] = char_style
        return char_styles

    def _extract_paragraphs(self):
        paragraph_nodes = self._xpath('//w:p')
        for paragraph_index, paragraph_node in enumerate(paragraph_nodes):
            paragraph = {
                'index': paragraph_index,
            }
            paragraph.update(self._get_paragraph_text_and_styles(paragraph_node))

            yield paragraph

    def _get_paragraph_text_and_styles(self, paragraph_node):
        text_parts = []
        index_start = 0
        style_ranges = OrderedDict()
        previous_style_id = None
        for text_node in self._xpath('w:r/w:t', element=paragraph_node):
            text_part = text_node.text
            if text_part is None:
                continue
            text_parts.append(text_part)
            index_end = index_start + len(text_part)
            style_id = self._xpath('w:rPr/w:rStyle/@w:val', element=text_node.getparent())
            if style_id:
                style_id = style_id[0]
                if style_id == previous_style_id:
                    (last_index_start, _), last_style = style_ranges.popitem(last=True)
                    style_ranges[(last_index_start, index_end)] = last_style
                else:
                    style_ranges[(index_start, index_end)] = self.styles[style_id]
            previous_style_id = style_id
            index_start = index_end
            #print(tTag)
        return {
            'text': ''.join(text_parts),
            'styles': style_ranges,
        }
        #pPr_node = self._xpath('w:pPr', element=paragraph_node)[0]


    def extractStyleToSmallCaps(self):
        '''
        This method extracts information on small caps from the document and 
        saves the information about indexes where small caps start and end into
        a dictionary. This mapping is then returned.
        '''
        result = {}
        #        print(self.domStyles)
        for child in self.styles:
            if child.get('w:type') == 'character':
                styleId = child.get('w:styleId')
                smallCapsTags = child.getElementsByTagName('w:smallCaps')
                if smallCapsTags:
                    if smallCapsTags[0].get('w:val') == 'on':
                        result[styleId] = True
                    else:
                        result[styleId] = False
                else:
                    result[styleId] = False
        return result

    def _xpath(self, expression, element=None):
        element = element or self.document
        if element is self.document:
            expression = '/w:wordDocument' + ('' if expression[0] == '/' else '/') + expression
        return element.xpath(expression, namespaces=self.namespaces)
