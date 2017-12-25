# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
import hashlib
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem
from scrapy import Request


class FilterPipeline(object):
    '''skip when image item already existed.'''
    db = None
    cursor = None

    def __init__(self, conf):
        try:
            self.db = pymysql.connect(conf['host'], conf['user'], conf['pass'], conf['name'], port=conf['port'], charset='utf8')
        except pymysql.OperationalError as e:
            print ("Mysql Operation Error[%d]: %s" % tuple(e))
            exit(0)
        self.cursor = self.db.cursor()

    def __del__(self):
        self.db.close()

    @classmethod
    def from_crawler(cls, crawler):
        '''static function'''
        return cls({
            'host' : crawler.settings.get('MYSQL_HOST'),
            'port' : crawler.settings.get('MYSQL_PORT'),
            'name' : crawler.settings.get('MYSQL_NAME'),
            'user' : crawler.settings.get('MYSQL_USER'),
            'pass' : crawler.settings.get('MYSQL_PASS')
        })

    def process_item(self, item, spider):
        # cats spider record
        sql = "SELECT id FROM cats_spider_log WHERE spider_sn=%s"
        self.cursor.execute(sql, (spider.sn,))
        row = self.cursor.fetchone()
        if row:
            id = str(row[0])
            self.cursor.execute("UPDATE cats_spider_log SET total_item_count=total_item_count+1 WHERE id=%s", (id,))
            self.db.commit()
        else:
            self.cursor.execute("INSERT INTO cats_spider_log (spider_name,spider_sn,page_start,page_end,total_item_count) VALUES (%s,%s,%s,%s,1)",
                                (spider.name, spider.sn, spider.start, spider.end)
                                )
            self.db.commit()
            id = str(self.cursor.lastrowid)
        item['img_spider'] = id
        item['img_hash'] = hashlib.md5(item['img_from'].encode()).hexdigest()
        sql = "SELECT id FROM cat_imgs WHERE img_hash=%s"
        self.cursor.execute(sql, (item['img_hash'], ))
        if self.cursor.fetchone():
            spider.log('HASH exists.')
            raise DropItem("HASH exists.")
        else:
            return item

class ImgsPipeline(ImagesPipeline):
    '''Download images'''

    def get_media_requests(self, item, info):
        # build request referer
        return Request(item['img_from'], headers={"Referer": info.spider.ref})

    def item_completed(self, results, item, info):

        for ok,x in results:
            if not ok:
                raise DropItem("Item contains no files")
            item['img_src'] = x['path']
            return item

class CatsPipeline(object):
    '''Save item to mysql'''
    db = None
    cursor = None

    def __init__(self, conf):
        try:
            self.db = pymysql.connect(conf['host'], conf['user'], conf['pass'], conf['name'], port=conf['port'], charset='utf8')
        except pymysql.OperationalError as e:
            print ("Mysql Operation Error[%d]: %s" % tuple(e))
            exit(0)
        self.cursor = self.db.cursor()

    def __del__(self):
        self.db.close()

    @classmethod
    def from_crawler(cls, crawler):
        '''private function'''
        return cls({
            'host' : crawler.settings.get('MYSQL_HOST'),
            'port' : crawler.settings.get('MYSQL_PORT'),
            'name' : crawler.settings.get('MYSQL_NAME'),
            'user' : crawler.settings.get('MYSQL_USER'),
            'pass' : crawler.settings.get('MYSQL_PASS')
        })

    def process_item(self, item, spider):

        # save img
        sql = "INSERT INTO cat_imgs (img_hash, img_src, img_desc, img_from) VALUES (%s, %s, %s, %s)"
        self.cursor.execute(sql, (item['img_hash'], item['img_src'], item['img_desc'], item['img_from']))
        self.db.commit()
        # update count
        self.cursor.execute("UPDATE cats_spider_log SET new_item_count=new_item_count+1 WHERE id=%s", (item['img_spider'],))
        self.db.commit()

        return item
