import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from absch.items import Article


class AbsSpider(scrapy.Spider):
    name = 'abs'
    start_urls = ['https://www.abs.ch/de/ueber-die-abs/die-abs-aktuell/aktuelle-meldungen/']

    def parse(self, response):
        links = response.xpath('//li[@class="listItem clearfix"]/a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//li[@class="pageBrowserListItem listItemForeward"]/a/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h3//text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//div[@class="newsSingle"]/span//text()').get()
        if date:
            date = date.strip()

        content = response.xpath('//div[@class="newsSingle"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content[2:]).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
