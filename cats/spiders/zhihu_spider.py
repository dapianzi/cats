import scrapy
import time
from cats.items import Imgs

class ZhihuSpider(scrapy.Spider):
    name = "zhihu"
    ref = "https://www.zhihu.com"

    def __init__(self, page_range='1-10', *args, **kwargs):
        super(ZhihuSpider, self).__init__(*args, **kwargs)

        self.sn = self.name + '-' + str(time.time())
        self.start,self.end = page_range.split('-')
        self.start_urls = ['https://www.zhihu.com/search?type=topic&q=猫']

    def writepage(self, res):
        f = open('temp.html', 'wb+')
        f.write(res.body)
        f.close()

    # 放弃登录
    def login(self, res):
        form_data = {
            '_xsrf' : res.xpath('//input[@name="_xsrf"]').extract_first(),
            'password' : '',
            'phone_num': '',
            'captcha_type' : 'cn',
        }
        cookie = {
            'Cookie': '_zap=a6dee6f4-091b-429c-97b7-9373bc35efe8; d_c0="ACACaThsVQyPTi03m9DJQ4I_EIQqkkQXFCQ=|1504671052"; _zap=0bf13779-eab2-49b8-95ef-fb7fa02a4d54; q_c1=87ee3816ee9242fa9ecb31ef8cc4226c|1507773458000|1490346554000; __utmz=51854390.1511413192.1.1.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; _xsrf=dbc083f6-fe45-412a-a017-c953c016d879; __utma=51854390.1281661096.1511413192.1511413192.1513932545.2; __utmb=51854390.0.10.1513932545; __utmc=51854390; r_cap_id="OTQ5YWJmZmJkMzNmNDY3Y2I4OWQ4ZDFmYjAxNTVhYjA=|1513934662|0d68e8663e2ebb9e075117660e8f03f3e3e25ff4"; cap_id="ZDBiOWUwY2Y4YTg4NGE1OWJhYTgyZjIyYTA5NWM3NmY=|1513934662|eac385b925e952f54d3d2075496ea39900fc9800"; __utmv=51854390.000--|2=registration_date=20161008=1^3=entry_date=20170324=1; l_cap_id="MDlmYzRkNmEyNWMyNDNkMmIxMzYxYjlhMGM3NDI1NTA=|1513934981|e6a2faf5dc760eac0d8f8732e93e4681318f2dca"'
        }
        return scrapy.http.FormRequest('https://www.zhihu.com/login/phone_num', formdata=form_data, callback=self.start_zhihu, cookies=cookie)

    def parse(self, res):
        #self.writepage(res)
        topic = res.css('a.TopicLink::attr(href)').extract_first()
        # https://www.zhihu.com/topic/19554935/top-answers?page=1
        for x in range(int(self.start), int(self.end)):
            yield scrapy.Request('https://www.zhihu.com%s/top-answers?page=%d' % (topic, x), callback=self.parse_question)

    def parse_question(self, res):
        #self.writepage(res)
        answers = res.css('div.zm-item-rich-text')
        for x in answers:
            # answer with photo
            if x.css('.summary img'):
                href = x.css('::attr(data-entry-url)').extract_first()
                yield scrapy.Request(self.ref + href, callback=self.parse_answer)

    def parse_answer(self, res):
        #self.writepage(res)
        img = res.css('.RichContent-inner img::attr(data-actualsrc)').extract()
        alt = res.xpath('//title/text()').extract_first()
        print (alt)
        for i in img:
            yield Imgs(img_from=i, img_desc=alt)