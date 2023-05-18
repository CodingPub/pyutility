#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import smtplib
import threading
import time
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
from utility.log import Log
from utility.common import Common
from utility.singleton import Singleton

__all__ = ('MailTool', 'send_mail')


class Mail(object):

    def __init__(self, receivers, title, content):
        self.receivers = receivers
        self.title = title
        self.content = content


class MailTool(object, metaclass=Singleton):

    def __init__(self):
        self._lock = threading.Lock()
        self._mails = []
        self._busy = False

        self._mail_host = None
        self._mail_user = None
        self._mail_password = None
        self._server = None

    def init(self, host, user, passowrd, name):
        self._lock.acquire()

        self._mail_host = host
        self._mail_user = user
        self._mail_password = passowrd
        self._mail_name = name

        self._lock.release()
        Log.debug('mail tool init')

    def send(self, receivers, title, content):
        mail = Mail(receivers, title, content)
        self._add_mail(mail)

        if self._busy:
            return
        self._lock.acquire()
        if self._busy:
            self._lock.release()
            return

        self._busy = True
        self._lock.release()

        t = threading.Thread(target=self._send_mails)
        # 主线程结束，邮件继续
        # t.setDaemon(True)
        t.start()

    def _send_mails(self):
        if not self._has_mail() or not self._login():
            return

        mail = self._get_first_mail()
        while mail:
            try:
                self._send_a_mail(mail.receivers, mail.title, mail.content)
            except Exception as e:
                Log.error('%s' % e)

            self._delete_mail(mail)
            mail = self._get_first_mail()
            if mail:
                time.sleep(1)

        self._logout()
        self._busy = False

    def _login(self):
        if self._server:
            Log.debug('邮件已登录')
            return True
        try:
            Log.debug('邮件登录... %s' % self._mail_host)
            server = smtplib.SMTP_SSL(self._mail_host, 465)  # SMTP协议默认端口是25
            server.set_debuglevel(0)
            server.ehlo()
            server.login(self._mail_user, self._mail_password)
            self._server = server
            Log.debug("mail login successfully")
            return True
        except Exception as e:
            Log.error('%s' % e)
        return False

    def _logout(self):
        if not self._server:
            return
        try:
            self._server.quit()
            self._server = None
            Log.debug("mail quit successfully")
        except Exception as e:
            Log.error('%s' % e)

    def _format_addr(self, s):
        name, addr = parseaddr(s)
        return formataddr((Header(name, 'utf-8').encode(), addr))

    def _send_a_mail(self, receivers, title, content):
        Log.info('发送邮件 %s\n%s\n%s', receivers, title, content)

        if not receivers or not title or not content:
            return

        if Common.debug():
            Log.info('debug 模式不发送邮件')
            return

        if isinstance(receivers, str):
            receivers = [receivers]

        sender = self._mail_user
        msg = MIMEText(content, 'plain', 'utf-8')
        msg['From'] = self._format_addr('%s <%s>' % (self._mail_name, sender))
        msg['To'] = ', '.join(['%s <%s>' % (x, x) for x in receivers])
        msg['Subject'] = Header(title, 'utf-8').encode()
        self._server.sendmail(sender, receivers, msg.as_string())
        Log.info("mail has been send successfully.")

    def _add_mail(self, mail):
        if not mail:
            return

        self._lock.acquire()
        self._mails.append(mail)
        self._lock.release()

    def _delete_mail(self, mail):
        if not mail:
            return

        self._lock.acquire()
        self._mails.remove(mail)
        self._lock.release()

    def _has_mail(self):
        count = 0
        self._lock.acquire()
        count = len(self._mails)
        self._lock.release()
        return count > 0

    def _get_first_mail(self):
        mail = None

        self._lock.acquire()
        if self._mails:
            mail = self._mails[0]
        self._lock.release()

        return mail


def send_mail(receivers, title, content):
    MailTool().send(receivers, title, content)


if __name__ == "__main__":
    mail_host = "smtp.163.com"  # SMTP服务器
    mail_user = "helper1840@163.com"  # 用户名
    mail_pass = "wy112233"  # 授权密码，非登录密码
    mail_name = "智能助手"  # 发件人标题

    receivers = ['lxb_0605@qq.com']

    MailTool().init(mail_host, mail_user, mail_pass, mail_name)

    for x in range(1, 2):
        send_mail(receivers, '人生苦短%s' % x, '我用Python')

    # time.sleep(60)
