# -*- coding: utf-8 -*-
import scrapy


class AviParseSpider(scrapy.Spider):
    name = 'avi_parse'
    start_urls = ['https://www.avito.ru/ryazan/kvartiry/sdam/na_dlitelnyy_srok?s_trg=4&user=1/']
    download_delay = 1.5

    def parse(self, response):
        # parse links to details page
        urls = response.css(
            'div.description.item_table-description > div.item_table-header > h3 > a::attr(href)').extract()
        # follow links to details
        for url in urls:
            url = response.urljoin(url)
            yield scrapy.Request(url=url, callback=self.parse_details)
        # follow next page
        next_page = response.css('a.js-pagination-next::attr(href)').extract_first()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_details(self, response):
        yield {
            'title': response.css('div.title-info-main > h1 > span::text').extract_first(),
            'date': response.css('div.title-info-metadata-item::text').extract_first(),
            'price': response.css('#price-value > span > span.js-item-price::text').extract_first(),
            'area': response.css('div.item-map-location > span.item-map-address > span::text').extract_first(),
            'address': response.css('div.item-map-location > span.item-map-address > span > span::text').extract_first()
        }
