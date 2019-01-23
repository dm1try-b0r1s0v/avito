# -*- coding: utf-8 -*-
import os
import scrapy
from selenium import webdriver
import base64
from PIL import Image
from time import sleep
import pytesseract


class AviParseSpider(scrapy.Spider):
    name = 'avi_parse'
    start_urls = ['https://www.avito.ru/ryazan/kvartiry/sdam/na_dlitelnyy_srok?s_trg=4&user=1/']

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

        # get ads id
        ads_date = response.css('div.title-info-metadata-item::text').extract_first()
        splitted_date = ads_date.split()
        ads_id = splitted_date[1]

        # Show phone image
        driver = webdriver.Chrome('/path/to/chromedriver')  # Of course you can use Firefox, IE
        driver.get(response.request.url)
        button = driver.find_element_by_xpath(
            '//a[@class="button item-phone-button js-item-phone-button button-origin button-origin-blue button-origin_full-width button-origin_large-extra item-phone-button_hide-phone item-phone-button_card js-item-phone-button_card"]')
        button.click()
        sleep(3)

        # get image
        image = driver.find_element_by_xpath('//div[@class="item-phone-big-number js-item-phone-big-number"]/img')

        # get image src
        image_src = image.get_attribute('src').split(',')[1]

        # convert image to bytes
        img = base64.decodebytes(bytearray(image_src, 'utf-8'))

        # save image
        with open('%s.png' % ads_id, 'wb') as f:
            f.write(img)
        driver.quit()

        # image recognition
        image_to_recon = Image.open('%s.png' % ads_id)
        phone = pytesseract.image_to_string(image_to_recon)

        # remove image file
        os.remove('%s.png' % ads_id)

        yield {
            'id': ads_id,
            'title': response.css('div.title-info-main > h1 > span::text').extract_first(),
            'date': ads_date,
            'price': response.css('#price-value > span > span.js-item-price::text').extract_first(),
            'area': response.css('div.item-map-location > span.item-map-address > span::text').extract_first(),
            'address': response.css(
                'div.item-map-location > span.item-map-address > span > span::text').extract_first(),
            'phone': phone,
        }
