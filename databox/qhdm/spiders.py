import re
from typing import Any

from scrapy import Spider, Request
from scrapy.http import Response

from databox.qhdm.items import Region


class AdministrativeDivisionSpider(Spider):
    REGION_CODE_REGEX = r'(\w+)\.html'
    REGION_CODE_REGEX_WITH_SLASH = r'\w+/(\w+)\.html'
    REGION_CODE_PATTERN = re.compile(REGION_CODE_REGEX)
    REGION_CODE_PATTERN_WITH_SLASH = re.compile(REGION_CODE_REGEX_WITH_SLASH)
    LEVELS = ['province', 'city', 'county', 'town', 'village']

    name = 'administrative_division'
    start_urls = ['https://www.stats.gov.cn/sj/tjbz/qhdm/']

    def parse(self, response: Response, **kwargs: Any) -> Any:
        """
        find latest region data homepage
        :param response:
        :param kwargs:
        :return:
        """
        li_elements = response.css('.list-content > ul > li')
        if li_elements:
            latest_standard_url = li_elements[0].css('a::attr(href)').get()
            latest_standard_time = li_elements[0].css('span::text').get().strip()
            yield Request(url=latest_standard_url, callback=self.parse_region, meta={
                'region_type_idx': 0,
                'update_time': latest_standard_time
            }, dont_filter=True)

    def parse_region(self, response):
        region_type = self.LEVELS[response.meta['region_type_idx']]
        selector = f".{region_type}table .{region_type}tr td:last-child a"
        regions = response.css(selector)
        for region in regions:
            if 'index.html' in response.url:
                pass
            href = region.css('::attr(href)').get()
            region_item = Region()
            region_item['code'] = self.href_to_region_code(href)
            region_item['name'] = region.css('::text').get()
            region_item['type'] = region_type
            if 'parent_code' in response.meta:
                region_item['parent_code'] = response.meta['parent_code']
            print(region_item)
            yield region_item
            if href is not None:
                next_level_url = self.href_to_next_level_url(response.url, href)
                yield Request(url=next_level_url, callback=self.parse_region, meta={
                    'parent_code': region_item['code'],
                    'region_type_idx': response.meta['region_type_idx'] + 1
                }, dont_filter=True)

    @staticmethod
    def href_to_region_code(href):
        if '/' in href:
            return AdministrativeDivisionSpider.REGION_CODE_PATTERN_WITH_SLASH.match(href).group(1)
        else:
            return AdministrativeDivisionSpider.REGION_CODE_PATTERN.match(href).group(1)

    @staticmethod
    def href_to_next_level_url(current_url, href):
        return re.sub(AdministrativeDivisionSpider.REGION_CODE_PATTERN, href, current_url)
