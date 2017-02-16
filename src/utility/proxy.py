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
from utility import pyinterfacer


__author__ = 'Lin Xiaobin'

__all__ = ['ProxyPool']

headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:39.0) Gecko/20100101 Firefox/39.0"}


_proxyIndex = 0


class ProxyPool(object, metaclass=Singleton):
    def __init__(self):
        super(ProxyPool, self).__init__()
        self.cache = ProxyCache()
        self.ips = self.cache.queryIP(ip=None)
        self.lock = threading.Lock()
        self.isScaning = False

    # 验证本地代理列表
    def vertifyAllProxies(self):
        self._vertifyProxies(self.ips, isLocal=True)
        self.scanProxies(minProxies=15)

    # 验证单个代理
    def vertifyProxy(self, ip, times=1):
        for x in range(times):
            if self._isProxyEable(ip):
                self._addProxy(ip)
                return
        self._deleteProxy(ip)
        self.scanProxies(minProxies=5)

    # 随机获取一个代理，代理不足时自动扫描
    def randProxy(self):
        result = None
        self.lock.acquire()
        count = len(self.ips)
        if count > 0:
            # 优先取前8个代理
            idx = random.randint(0, min([count, 8]) - 1)
            result = self.ips[idx]
        self.lock.release()
        return result

    def scanProxies(self, minProxies):
        if self.isScaning:
            return
        else:
            self.isScaning = True

        if isDebug():
            self.get_from_ipcn()
            # self.get_from_xicidaili()
            # self.get_from_kxdaili()
            # self.get_from_66ip()
            pass
        else:
            methods = [self.get_from_ipcn,
                       self.get_from_kxdaili,
                       self.get_from_xicidaili]
            for scan in methods:
                if len(self.ips) < minProxies:
                    scan()

            # 海外
            # self.get_from_66ip()
        self.isScaning = False

    def cleanAllProxy(self):
        self.lock.acquire()
        self.ips = []
        self.cache.cleanAllIP()
        self.lock.release()

    def get_from_ipcn(self):
        # 海外 'http://proxy.ipcn.org/proxya2.html', 'http://proxy.ipcn.org/proxyb2.html'
        urls = ['http://proxy.ipcn.org/proxya.html', 'http://proxy.ipcn.org/proxyb.html']

        for url in urls:
            html = pyinterfacer.requestString(url, headers=headers)
            ips = rexFindAll('\d+\.\d+\.\d+\.\d+:\d+', html)
            self._vertifyProxies(ips)

    def get_from_xicidaili(self):
        urls = ['http://www.xicidaili.com/nn/',
                'http://www.xicidaili.com/nn/2', 'http://www.xicidaili.com/wn/']
        for url in urls:
            html = pyinterfacer.requestString(url, headers=headers)
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
                html = pyinterfacer.requestString(url % (page), headers=headers)
                page += 1

                table = htmlElements(html, '//*[@id="nav_btn01"]/div[6]/table/tbody/tr')
                # print(table)
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
            html = pyinterfacer.requestString(url, headers=headers)
            iplist = rexFindAll('\d+\.\d+\.\d+\.\d+:\d+', html)
            self._vertifyProxies(iplist)

    def _vertifyProxies(self, array, isLocal=False):
        if array is None:
            return

        nl = array[:]
        multiRun(self._vertifyOneProxy, nl, 10, '', '', args={'isLocal': isLocal})

    def _vertifyOneProxy(self, array, index, args=None):
        proxy = array[index]
        if args.get('isLocal') or proxy not in self.ips:
            self.vertifyProxy(proxy)
        else:
            print('pass check', proxy)

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

    def cleanAllIP(self):
        cmd = 'delete from enableips'
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
    print(len(pool.ips))
    pool.vertifyAllProxies()
    print(len(pool.ips))

    pass
