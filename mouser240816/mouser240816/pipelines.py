# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymysql
import openpyxl
import time
import os

class Mouser240816DbPipeline:
    def __init__(self):
        self.conn = pymysql.connect(host='localhost', port=3306,
                                  user='root', password='123456',
                                  db ='mouser', charset='utf8')
        self.cursor = self.conn.cursor()
        self.data = []
        # self.cursor.execute(
        #     'drop database if exists mouser'
        # )
        # self.cursor.execute(
        #     'create database if not exists mouser default charset utf8'
        # )
        # self.conn.commit()
        self.conn.select_db('mouser')

        # self._check_db_create()
        self.re_create_db()

    def re_create_db(self):
        self.cursor.execute(
            'drop table if exists mouser_mfr_links;'
        )
        self.cursor.execute(
            'create table mouser_mfr_links ('
            'id int unsigned primary key auto_increment,'
            'mfr_name varchar(255),'
            'mfr_link varchar(255),'
            'all_products_url varchar(255)'
            ');'
        )
        self.conn.commit()

    def _check_db_create(self):
        self.cursor.execute("SHOW TABLES LIKE 'mouser_mfr_links'")
        table_exists = self.cursor.fetchone()
        if not table_exists:
            self.cursor.execute(
                'create table mouser_mfr_links ('
                'id int unsigned primary key auto_increment,'
                'mfr_name varchar(255),'
                'mfr_link varchar(255),'
                'all_products_url varchar(255)'
                ');'
            )
        self.conn.commit()

    def close_spider(self, spider):
        # self.conn.commit()
        if len(self.data) >0:
            self._write_to_db()
        self.conn.close()

    def _check_and_delete_existing_data(self, mfr_name):
        # 检查是否存在相同名字的厂家
        self.cursor.execute('SELECT id FROM mouser_mfr_links WHERE mfr_name = %s', (mfr_name))
        result = self.cursor.fetchone()
        if result:
            # 删除旧数据
            self.cursor.execute('DELETE FROM mouser_mfr_links WHERE mfr_name = %s', (mfr_name))

    def _write_to_db(self):
        for item in self.data:
            mfr_name = item[0]
            # 调用新方法检查并删除旧数据
            self._check_and_delete_existing_data(mfr_name)
            # 插入新数据
            self.cursor.execute(
                'INSERT INTO mouser_mfr_links (mfr_name, mfr_link, all_products_url) VALUES (%s, %s, %s)',
                item
            )
        self.data.clear()
        self.conn.commit()
    # def _write_to_db(self):
    #     self.cursor.executemany(
    #         'insert into mouser_mfr_links (mfr_name, mfr_link, all_products_url) values (%s,%s, %s) '
    #         , self.data)
    #     self.conn.commit()


    def process_item(self, item, spider):
        mfr_name = item.get('mfr_name', '')
        mfr_link = item.get('mfr_link', '')
        all_products_url = item.get('all_products_url', '')
        self.data.append((mfr_name, mfr_link, all_products_url))
        if len(self.data) == 10:
            self._write_to_db()
            self.data.clear()
        return item

class ExcelPipeline:
    def __init__(self):

        self.file_path = 'mouser_links.xlsx'
        if os.path.exists(self.file_path):
            self.wb = openpyxl.load_workbook(self.file_path)
            self.ws = self.wb.active
        else:
            self.wb = openpyxl.Workbook()
            self.ws = self.wb.active
            self.ws.title = 'mouser_links'
            self.ws.append(['mfr_name', 'mfr_link', 'all_products_url'])

    def close_spider(self, spider):
        self.wb.save('mouser_links.xlsx')  # 修改为相对路径

    def process_item(self, item, spider):
        mfr_name = item.get('mfr_name', '')
        mfr_link = item.get('mfr_link', '')
        all_products_url = item.get('all_products_url', '')
        self.ws.append((mfr_name, mfr_link, all_products_url))
        return item
