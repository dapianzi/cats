import scrapy
import time
from cats.items import Imgs

class SupervrSpider(scrapy.Spider):
    name = "supervr"
    ref = "http://www.supervr.net"

    def __init__(self, page_range='1-10', *args, **kwargs):
        super(SupervrSpider, self).__init__(*args, **kwargs)

        self.sn = self.name + '-' + str(time.time())
        self.start,self.end = page_range.split('-')
        urls = [
            'http://www.supervr.net/catbbs/forums/show/2/%d.page',
            'http://www.supervr.net/catbbs/forums/show/4/%d.page',
            'http://www.supervr.net/catbbs/forums/show/10/%d.page',
            'http://www.supervr.net/catbbs/forums/show/11/%d.page',
        ]
        self.start_urls = []
        for x in range(int(self.start), int(self.end)):
            for u in urls:
                self.start_urls.append(u % x)

    def writepage(self, res):
        f = open('temp.html', 'wb+')
        f.write(res.body)
        f.close()

    def parse(self, res):
        #self.writepage(res)
        for topic in res.css('.topictitle'):
            # only pic topic
            if topic.xpath('./following-sibling::img'):
                href = topic.css('::attr(href)').extract_first()
                yield scrapy.http.Request(self.ref + href, callback=self.parse_img)

    def parse_img(self, res):
        alt = res.css('title::text').extract_first()
        for x in res.css('.row2 a img'):
            src = x.css('::attr(src)').extract_first()
            if src.find('_thumb') != -1:
                src = src.replace('_thumb', '')
                # return multiple items from one single callback
                yield Imgs(img_from=self.ref + src, img_desc=alt)