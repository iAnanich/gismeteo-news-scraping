from scrapy.selector import SelectorList


class Extractor:
    """
    Extracts data from HTML using `scrapy.selector.SelectorList.css method.
    """

    replace_with = []
    allowed_ends = []

    def __init__(self, string_css_selector=None,
                 list_of_string_css_selectors: list =None,
                 **kwargs):
        if string_css_selector:
            self._check_string_selector(string_css_selector)
            self.list_of_string_selectors = [string_css_selector]
        elif list_of_string_css_selectors:
            for item in list_of_string_css_selectors:
                self._check_string_selector(item)
            self.list_of_string_selectors = list_of_string_css_selectors
        self.kwargs = {}
        self.parse_kwargs(kwargs)

    def parse_kwargs(self, kwargs):
        pass

    def _check_string_selector(self, string_selector: str):
        if not isinstance(string_selector, str):
            raise TypeError('Given `string_selector` argument isn\'t `str`.')
        for end in self.allowed_ends:
            if string_selector.endswith(end):
                break
        else:
            raise ValueError(
                'Given `string_selector` (="{}") argument'
                .format(string_selector))

    def _format(self, text: str) -> str:
        for before, after in self.replace_with:
            text = text.replace(before, after)
        return text

    def select_from(self, selector: SelectorList) -> SelectorList:
        raise NotImplementedError

    def extract_from(self, selector: SelectorList) -> str:
        raise NotImplementedError


# ===================
#  actual extractors
# ===================
class HeaderExtractor(Extractor):

    _name = 'header'

    allowed_ends = ['::text']

    def select_from(self, selector: SelectorList) -> SelectorList:
        return selector.css(self.list_of_string_selectors[0])

    def extract_from(self, selector: SelectorList) -> str:
        extracted = self.select_from(selector).extract_first()
        formatted = self._format(extracted)
        return formatted


class TagExtractor(HeaderExtractor):

    _name = 'tag'

    default = ''
    separator = ', '

    def _convert(self, lst: list) -> str:
        if len(lst) == 0:
            return self.default
        string = self._format(lst[0])
        for item in lst[1:]:
            formatted = self._format(item)
            if formatted:
                string += self.separator + self._format(item)
        return string

    def select_from(self, selector: SelectorList) -> SelectorList:
        found_list = []
        found_indexes = []
        for i, string_selector in enumerate(self.list_of_string_selectors):
            selected = selector.css(string_selector)
            if selected:
                found_indexes.append(i)
                found_list.append(selected)
            else:
                found_list.append(None)
        if len(found_indexes) == 1:
            return found_list[found_indexes[0]]
        elif len(found_indexes) > 1:
            raise RuntimeError('Found more than one "{name}" containers: {lst}'
                               .format(lst=found_list, name=self._name))
        else:
            raise RuntimeError('Not found any "{}" containers.'
                               .format(self._name))

    def extract_from(self, selector: SelectorList) -> str:
        extracted = self.select_from(selector).extract()
        converted = self._convert(extracted)
        return converted


class TextExtractor(TagExtractor):

    _name = 'text'

    separator = '\n'
    replace_with = [
        ('\xa0', ' '),
        ('\r\n\t', ''),
        ('\t', ' '),
        ('\n', ' '),
    ]
    allowed_ends = ['div']

    def extract_from(self, selector: SelectorList):
        selected = self.select_from(selector)
        elements = []
        for div in selected:
            link = div.css('div > a::text')
            picture = div.css('div > div.pic-descr::text')
            if link:
                link_extracted = link.extract_first()
                href_extracted = div.css('div > a::attr(href)').extract_first()
                for item in div.css('::text').extract():
                    if item == link_extracted:
                        elements.append(' [{0}]({1}) '.format(
                            link_extracted,
                            href_extracted, ))
                    else:
                        elements.append(item)
            elif picture:
                elements.append('<photo>')
            else:
                elements.append(div.css('div::text').extract_first())
        formatted = self._convert(elements)
        return formatted


class LinkExtractor(Extractor):

    _name = 'link'

    replace_with = []
    allowed_ends = ['a::attr(href)']

    def select_from(self, selector: SelectorList):
        for string_selector in self.list_of_string_selectors:
            selected = selector.css(string_selector)
            if selected:
                for item in selected:
                    yield item
            else:
                raise RuntimeError(
                    '`{}` selector failed'.format(string_selector))

    def extract_from(self, selector: SelectorList):
        for selected in self.select_from(selector):
            yield self._format(selected.extract())
