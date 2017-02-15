#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tempfile
import threading
import time
import requests
import random
import tempfile
from utility.common import *
from utility.singleton import *
from utility.logger import *
from utility.dbcache import *
from utility.pyinterfacer import *


__author__ = 'Lin Xiaobin'

__all__ = ['ProxyPool']

headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:39.0) Gecko/20100101 Firefox/39.0"}


class ProxyPool(object, metaclass=Singleton):
    def __init__(self):
        super(ProxyPool, self).__init__()
        self.cache = ProxyCache()
        self.ips = self.cache.queryIP(ip=None)
        self.lock = threading.Lock()

    # 验证本地代理列表，代理个数不足30时重新扫描
    def vertifyAllProxies(self):
        self._vertifyProxies(self.ips)
        if len(self.ips) < 30:
            self.scanProxies()

    # 验证单个代理
    def vertifyProxy(self, ip, times=2):
        for x in range(times):
            if self._isProxyEable(ip):
                self._addProxy(ip)
                return
        self._deleteProxy(ip)

    # 随机获取一个代理，代理不足时自动扫描
    def randProxy(self):
        result = None
        self.lock.acquire()
        count = len(self.ips)
        if count > 0:
            result = self.ips[random.randint(0, count - 1)]
        self.lock.release()
        return result

    def scanProxies(self):
        if isDebug():
            self.get_from_ipcn()
            # self.get_from_xicidaili()
            # self.get_from_kxdaili()
            # self.get_from_66ip()
            pass
        else:
            self.get_from_kxdaili()
            self.get_from_xicidaili()
            self.get_from_ipcn()

            # 海外
            # self.get_from_66ip()

    def get_from_ipcn(self):
        # 海外 'http://proxy.ipcn.org/proxya2.html', 'http://proxy.ipcn.org/proxyb2.html'
        urls = ['http://proxy.ipcn.org/proxya.html', 'http://proxy.ipcn.org/proxyb.html']

        for url in urls:
            html = requestString(url, headers=headers)
            ips = rexFindAll('\d+\.\d+\.\d+\.\d+:\d+', html)
            self._vertifyProxies(ips)

    def get_from_xicidaili(self):
        urls = ['http://www.xicidaili.com/nn/',
                'http://www.xicidaili.com/nn/2', 'http://www.xicidaili.com/wn/']
        for url in urls:
            html = requestString(url, headers=headers)
            table = htmlElements(html, '//*[@id="ip_list"]/tr')[1:]
            iplist = []
            for tr in table[1:]:
                tds = tr.getchildren()
                ip = tds[1].text + ':' + tds[2].text
                iplist.append(ip)
            self._vertifyProxies(iplist)

    def get_from_kxdaili(self):
        # 海外 'http://www.kxdaili.com/dailiip/3/%s.html'
        urls = ['http://www.kxdaili.com/dailiip/1/%s.html']
        for url in urls:
            page = 1
            while page <= 10:
                html = requestString(url % (page), headers=headers)
                page += 1

                table = htmlElements(html, '//*[@id="nav_btn01"]/div[6]/table/tbody/tr')
                print(table)
                if table is not None:
                    table = table[1:]
                    iplist = []
                    for tr in table[1:]:
                        tds = tr.getchildren()
                        ip = tds[0].text + ':' + tds[1].text
                        iplist.append(ip)
                    self._vertifyProxies(iplist)

    def get_from_66ip(self):
        urls = ['http://www.66ip.cn/nmtq.php?getnum=600&isp=0&anonymoustype=3&start=&ports=&export=&ipaddress=&area=0&proxytype=0&api=66ip']
        for url in urls:
            html = requestString(url, headers=headers)
            iplist = rexFindAll('\d+\.\d+\.\d+\.\d+:\d+', html)
            self._vertifyProxies(iplist)

    def _vertifyProxies(self, array):
        if array is None:
            return

        nl = array[:]
        multiRun(self._vertifyOneProxy, nl, 10, '', '')

    def _vertifyOneProxy(self, array, index, args=None):
        self.vertifyProxy(array[index])

    def _addProxy(self, ip):
        if ip is None:
            return

        self.lock.acquire()
        if ip not in self.ips:
            print('add ip:', ip)
            self.ips.append(ip)
            self.cache.addIP(ip)
        self.lock.release()

    def _deleteProxy(self, ip):
        if ip is None:
            return

        self.lock.acquire()
        if ip in self.ips:
            print('delete ip:', ip)
            self.ips.remove(ip)
            self.cache.deleteIP(ip)
        self.lock.release()

    def _isProxyEable(self, ip):
        if ip is None:
            return False

        proxies = {'http': 'http://%s' % ip}
        try:
            html = requests.get('http://httpbin.org/ip', proxies=proxies, timeout=5).text
            result = eval(html)['origin']
            # print(result)
            if len(result.split(',')) == 2:
                return False
            return result in ip
        except Exception as e:
            return False


class ProxyCache(DBCache):
    def __init__(self):
        directory = joinPaths(tempfile.gettempdir(), 'pyproxy')
        createdir(directory)
        dbPath = joinPaths(directory, 'proxy.db')
        print('proxy db:', dbPath)
        super(ProxyCache, self).__init__(dbPath)

        self.createDB()

    def createDB(self):
        cmd = '''create table if not exists enableips(ip char(50) primary key, date char(50))'''
        self._updateSQL(cmd, commit=True)

    def addIP(self, ip):
        items = self.queryIP(ip=ip)
        if items and len(items) > 0:
            return
        date = time.strftime('%Y-%m-%d %X', time.localtime())
        cmd = 'insert into enableips(ip, date) values("%s", "%s")' % (ip, date)

        self._updateSQL(cmd, commit=True)

    def deleteIP(self, ip):
        if ip is None:
            return

        cmd = 'delete from enableips where ip="%s"' % ip
        self._updateSQL(cmd, commit=True)

    def queryIP(self, ip=None):
        cmd = 'select ip from enableips where 1=1 '
        if ip:
            cmd += 'and ip="%s" ' % ip
        values = self._querySQL(cmd, commit=False)

        if values is None:
            return []
        else:
            return [x[0] for x in values if x is not None and len(x) > 0]


if __name__ == '__main__':
    # setDebug(True)

    pool = ProxyPool()
    # pool.scanProxies()
    # pool.vertifyAllProxies()
    print(pool.randProxy())

    pass
