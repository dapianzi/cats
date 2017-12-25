import scrapy
import time
from cats.items import Imgs

class InsSpider(scrapy.Spider):
    name = "instagram"
    ref = "https://www.instagram.com"

    def __init__(self, page_range='1-10', *args, **kwargs):
        super(InsSpider, self).__init__(*args, **kwargs)

        self.sn = self.name + '-' + str(time.time())
        self.start,self.end = page_range.split('-')
        urls = [
            'https://www.instagram.com/search/cats',
        ]
        self.start_urls = urls

    def writepage(self, res):
        f = open('temp.html', 'wb+')
        f.write(res.body)
        f.close()

    def parse(self, res):
        # todo
        pass
