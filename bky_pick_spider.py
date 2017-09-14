#liuxining
#2017年08月27日10:21:46

#爬取博客园精华区文章

import requests
import re
import time

from bky_pick.store import Store

class Bky_pick_spider(object):


    def __init__(self):
        self.post_data = {
            'CategoryId': -2,
            'CategoryType': 'Picked',
            'ItemListActionName': 'PostList',
            'PageIndex': 1,
            'ParentCategoryId': 0,
            'TotalPostCount': 1566
        }
        self.url = 'https://www.cnblogs.com/mvc/AggSite/PostList.aspx'
        self.page_num = 0
        self.article_num = 0

    #下载页面，返回页面内容
    def download(self,url,post_data):
        response = requests.get(url,data=post_data)
        return response.text



    #解析文本，解析出该页所有的文章并保存到数据库，返回下一页的页码，如果没有下一页，则返回None
    def parse(self,text):
        # (推荐数量，文章url,文章标题，作者url，作者名称，发布时间，评论数量，阅读数量)
        pattern = re.compile(r'<span class="diggnum".*?>(\d+)</span>.*?<div class="post_item_body">.*?<a class="titlelnk" href="(.*?)" target="_blank">(.*?)</a>.*?<div class="post_item_foot">.*?<a href="(.*?)" class="lightblue">(.*?)</a>.*?发布于\s(.*?)\s\r\n.*?评论\((.*?)\)</a>.*?阅读\((.*?)\)</a>',re.S)
        search_result = re.findall(pattern, text)
        print("爬取到 %d 篇文章" % len(search_result))

        for item in search_result:
            data = {
                'diggnum':item[0],
                'article_url':item[1],
                'article_title':item[2],
                'author_url':item[3],
                'author_name':item[4],
                'post_time':item[5],
                'comment_num':item[6],
                'view_num':item[7]
            }
            result = Store.save2mysql('localhost','root','490272','bky_spider','pick_article',data)
            if result == 'success':
                print('文章 "%s" 保存到数据库成功！' % item[2])
                self.article_num += 1
            else:
                print('文章 "%s" 保存到数据库失败，失败原因：%s！' % (item[2],result))

    def begin(self):
        print("开始爬取")
        for index in range(1,80):
            post_data = self.post_data
            post_data['PageIndex'] = index
            print('开始爬取第 %d 页' % post_data['PageIndex'])
            text = self.download(self.url,post_data)
            self.parse(text)
            self.page_num += 1
            time.sleep(1.5)
        print('爬取结束！共爬取 %d 页，%d 篇文章' % (self.page_num,self.article_num))


if __name__ == "__main__":
    bky_pick_spider = Bky_pick_spider()
    begin_time = time.time()
    bky_pick_spider.begin()
    end_time = time.time()
    print("程序退出,共耗时 %s 秒" % (end_time - begin_time))