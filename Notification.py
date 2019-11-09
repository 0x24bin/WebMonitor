# -*- coding:utf-8 -*-

from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import smtplib
from config import get
from log import logger
import traceback
import os







from_addr = get('mail','from')
password = get('mail','password')
to_addr = get('mail','to')
smtp_server = get('mail','host').strip()

smtp_port = get('mail','port').strip()

class Notification(object):
    def __init__(self, subject, to=None):
        """
        Initialize notification class
        :param subject:
        :param to:
        """
        self.subject = subject
        self.mail = get('mail','from')
        if to is None:
            self.to = get('mail', 'to')
        else:
            self.to = to


    # 字节bytes转化kb\m\g   返回大小单位为M
    def formatSize(self,bytes):
        try:
            bytes = float(bytes)
            kb = bytes / 1024
        except:
            print("传入的字节格式不对")
            return "Error"

        M = kb / 1024
        return M

    # 获取文件大小
    def getFileSize(self,path):
        try:
            if os.path.isfile(path):
                size = os.path.getsize(path)
            else:
                size = 0
            return self.formatSize(size)
        except Exception as err:
            print(err)


    def sendmail(self, html=None,attchfile=None):
        """
        Send notification use by mail
        :param html:
        :return:
        """
        msg = MIMEMultipart()
        msg['Subject'] = self.subject
        msg['From'] = '{0} <{1}>'.format(self.mail, get('mail', 'from'))
        # 支持多用户接收邮件
        msg['To'] = self.to


        text = MIMEText(html, 'html', 'utf-8')
        msg.attach(text)
        host = get('mail', 'host').strip()
        port = get('mail', 'port').strip()
        #print(attchfile)
        if attchfile:
            #只允许小于40Mb的附件
            if self.getFileSize(attchfile) < 40:
                #print('ok')
                zipApart = MIMEApplication(open(attchfile, 'rb').read())
                zipApart.add_header('Content-Disposition', 'attachment', filename=attchfile)
                msg.attach(zipApart)

        try:
            if port == '465':
                port = int(port)
                s = smtplib.SMTP_SSL(host, port)
            else:
                s = smtplib.SMTP(host, port)
                s.ehlo()
                s.starttls()
            s.ehlo()
            s.set_debuglevel(1)
            s.login(self.mail, get('mail', 'password'))
            s.sendmail(self.mail, self.to.split(','), msg.as_string())
            s.quit()
            return True
        except SMTPException:
            logger.critical('Send mail failed')
            traceback.print_exc()
            return False



if __name__ == '__main__':
    aa =Notification('aaa')
    aa.sendmail(html='<html>aaaaa</html>',attchfile='a.py')
