import scrapy
import time
import re
from cats.items import Imgs
from scrapy.selector import Selector

class TiebaSpider(scrapy.Spider):
    name = "tieba"
    ref = "http://tieba.baidu.com"

    def __init__(self, page_range='1-10', *args, **kwargs):
        super(TiebaSpider, self).__init__(*args, **kwargs)

        self.sn = self.name + '-' + str(time.time())
        self.start,self.end = page_range.split('-')
        urls = [
            'http://tieba.baidu.com/f?kw=猫咪&ie=utf-8&pn=%d',
        ]
        self.start_urls = ['http://tieba.baidu.com/f?kw=猫咪',]
        # for x in range(int(self.start), int(self.end)):
        #     for u in urls:
        #         self.start_urls.append(u % ((x-1)*50))

    def writepage(self, res):
        f = open('temp.html', 'wb+')
        f.write(res.body)
        f.close()

    def parse(self, res):
        # xpath stronger than css
        thread_list = res.xpath('//code[@id="pagelet_html_frs-list/pagelet/thread_list"]').extract_first()
        exp = re.compile(r'<code.*><!--(.*)--></code>', re.I|re.M|re.S)
        thread_list = re.sub(exp, r'\1', thread_list)
        topic = Selector(text=thread_list).xpath('//li[@class=" j_thread_list clearfix"]')
        for t in topic:
            # only pic topic
            if t.css('ul.threadlist_media'):
                href = t.css('a.j_th_tit::attr(href)').extract_first()
                yield scrapy.http.Request(self.ref + href, callback=self.parse_topic)

    def parse_topic(self, res):
        self.writepage(res)
        alt = res.css('h1.core_title_txt::text').extract_first()
        print (alt)
        for x in res.css('img.BDE_Image'):
            src = x.css('::attr(src)').extract_first()
            print (src)
            # return multiple items from one single callback
            yield Imgs(img_from=src, img_desc=alt)