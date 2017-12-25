import re
import scrapy
import time
from cats.items import Imgs

class Cats27270Spider(scrapy.Spider):
    name = "27270"
    ref = "http://www.27270.com"

    def __init__(self, page_range='1-10', *args, **kwargs):
        super(Cats27270Spider, self).__init__(*args, **kwargs)

        self.sn = self.name + '-' + str(time.time())
        self.start, self.end = page_range.split('-')

        urls = []
        for x in range(1, 5):
            urls.append('http://www.27270.com/zt/maomi/%d/' % x)
        self.start_urls = urls

    def parse(self, res):
        for topic in res.css('.picBox a'):
           href = topic.css('::attr(href)').extract_first()
           yield scrapy.http.Request(href, callback=self.parse_img)

    def parse_img(self, res):
        max = res.css('#pageinfo::attr(pageinfo)').extract_first()
        img = res.css('#picBody img')
        alt = img.css('::attr(alt)').extract_first()
        src = img.css('::attr(src)').extract_first()
        src = re.sub(r'\/(\d+)(\.jpg|\.png)', r"/%d\2", src)
        for x in range(1, int(max)+1):
            yield Imgs(img_from=src % x, img_desc=alt)
