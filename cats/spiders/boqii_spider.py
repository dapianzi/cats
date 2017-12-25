import scrapy
import time
from cats.items import Imgs

class BoqiiSpider(scrapy.Spider):
    name = "boqii"
    ref = "http://bbs.boqii.com"

    def __init__(self, page_range='1-36', *args, **kwargs):
        super(BoqiiSpider, self).__init__(*args, **kwargs)

        self.sn = self.name + '-' + str(time.time())
        self.start, self.end = page_range.split('-')

        urls = []
        for x in range(int(self.start), int(self.end)):
            urls.append('http://bbs.boqii.com/meitu/6-%d.html?sync=1' % x)
        self.start_urls = urls

    def parse(self, res):
        for topic in res.css('.img_title a'):
            href = topic.css('::attr(href)').extract_first()
            yield scrapy.http.Request(href, callback=self.parse_img)

    def parse_img(self, res):
        for x in res.css('.BigPbox img'):
            src = x.css('::attr(src)').extract_first()
            if src.find('_thumb') != -1:
                src = src.replace('_thumb', '')
                alt = x.css('::attr(alt)').extract_first()
                # return multiple items from one single callback
                yield Imgs(img_from=src, img_desc=alt)