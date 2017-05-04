#! usr/bin/env python3
# -*- coding:utf-8 -*-

__author__ = 'Qi'
__date__ = '2017-05-02'

import os
import re
import requests
import random
import time
from lxml import etree

class DownloadMeizitu(object):
    """
    下载“妹子图”网址下极品分类中的所有图片
    """
    def __init__(self, url=None):
        self.url = url

    def config_user_agent(self):
        """
        为每一次请求构造浏览器响应头
        """
        user_agent_list = [
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
            "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
            "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"]
        UA = random.choice(user_agent_list)
        headers = {'User-Agent': UA}
        return headers

    def config_proxy(self):
        """
        为每一次请求构造代理IP
        """
        ip_html = requests.get('http://haoip.cc/tiqu.htm')
        iplist = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,4}', ip_html.text)
        ip = random.choice(iplist).strip()
        proxies = {'http': ip}
        return proxies

    def request_page(self, single_url):
        """
        返回具体图片地址的二进制内容，用于下载
        """
        # proxy = self.config_proxy()
        headers = self.config_user_agent() 
        data = requests.get(single_url, headers=headers)
        data.encoding = 'gb2312'
        return data.content

    def get_selector(self, page_url):
        """
        获取网页页面的XML文档的节点对象
        """
        # proxy = self.config_proxy()
        headers = self.config_user_agent() 
        data = requests.get(page_url, headers=headers)
        data.encoding = 'gb2312'
        selector = etree.HTML(data.text)
        return selector

    def get_page(self):
        """
        获取妹子图“极品分类”中各分类的名称和地址
        """
        selector = self.get_selector(self.url)
        urls = selector.xpath('//div[@class="topmodel"]/ul/li/a/@href')
        names = selector.xpath('//div[@class="topmodel"]/ul/li/a/@title')
        return urls, names

    def get_specific_url(self):
        """
        获取各分类页面下各个子页面的地址
        """
        # 只提取urls，不需要names
        urls = self.get_page()[0]
        integrated_url = []
        for each_page_url in urls:
            selector = self.get_selector(each_page_url)
            # 获取各分类页面下的最大页数
            try:
                max_page = selector.xpath('//div[@id="wp_page_numbers"]/ul/li[last()]/a/@href')[0]
            except IndexError:
                break
            else:
                # print(each_page_url)
                # print(max_page)
                # 用正则表达式提取最大页数
                max_number = re.search(r'\d{1,2}(?=\.html)', max_page)
                for number in range(int(max_number[0])): # 第0个子组,即匹配的内容
                    integrated_url.append(self.url + max_page.replace(max_number[0], str(number+1)))
                # print(max_number)
        return integrated_url

    def get_pic_url(self):
        """
        获取子页面下图片组的地址
        """
        for each_integrated_url in self.get_specific_url():
            pic_url = []
            selector = self.get_selector(each_integrated_url)
            # 设置延时访问
            time.sleep(0.5)
            pic_url.extend(selector.xpath('//li[@class="wp-item"]/div/div/a/@href'))
            # print(pic_url)
            yield pic_url

    def download_every_pic(self):
        """
        获取每张图片的具体地址，并下载保存
        """
        '''
        val = True
        while val == True:
            try:
                result = next(self.get_pic_url())
            except StopIteration:
                val = False
                break
            else:
        '''
        result = next(self.get_pic_url())
        for every_single_pic in result:
            if every_single_pic:
                time.sleep(0.5)
                selector = self.get_selector(every_single_pic)
                
                every_single_pic_url = selector.xpath('//div[@id="picture"]/p/img/@src')
                every_single_pic_name = selector.xpath('//div[@id="picture"]/p/img/@alt')

                path = 'F:\\SpiderData\\妹子图\\'
                os.chdir(path)
                for i in range(len(every_single_pic_url)):
                    with open(path + every_single_pic_name[i] + '('+str(i+1)+')' + '.jpg', 'wb') as f:
                        time.sleep(0.5)
                        print('正在下载名为:"%s"的图片，请稍后...' % (every_single_pic_name[i] + '('+str(i+1)+')'))
                        f.write(self.request_page(every_single_pic_url[i]))
                        print('名为:"%s"的图片下载完成，准备下载下一张...\n' % (every_single_pic_name[i] + '('+str(i+1)+')'))

        print('下载完成!')

start = time.time()

if __name__ == '__main__':
    base_url = 'http://www.meizitu.com'
    DM = DownloadMeizitu(base_url)
    # urls, names = get_page(url)
    # print(urls, names)
    DM.download_every_pic()
    #print(config_proxy())
    #print(len(DM.get_pic_url()))
    # print(len(get_pic_url(url)))

stop = time.time()
# 计算程序用时
print('下载图片共用时:%.2f秒' % (stop-start))
