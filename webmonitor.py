# -*- coding:utf-8 -*-

import requests
from RequestsHeader import req_headers
from read_DB import *
from Notification import Notification
import random
from log import logger
import hashlib
from config import *
import multiprocessing as mp
from WebpageShot import webshot
import time
import os
import zipfile



class WebpageMonitor(object):
    def __init__(self):
        self.rules = get_rules()
        self.recorddir = get('default', 'recorddir').strip()
        self.fail_time_interval_num = int(get('default', 'FailTimeInterval').strip())
        self.timeinterval= int(get('default', 'TimeInterval'))
        self.retriesnum = int(get('default', 'retriesnum').strip())
        self.dbfile= get('default', 'dbfile')
        self.table_name = 'result'
        # 入库
        try:
            create_table('%s' % self.dbfile, 'result')
        except:
            pass


    def md5_ncrypt(self,text):
        m = hashlib.md5()
        m.update(text.encode(encoding='utf-8'))
        str_md5 = m.hexdigest()
        return str_md5

    def md5sum(self,filename, blocksize=65536):
        hash = hashlib.md5()
        with open(filename, "rb") as f:
            # 必须是rb形式打开的，否则的两次出来的结果不一致
            for block in iter(lambda: f.read(blocksize), b""):
                hash.update(block)
        return hash.hexdigest()

    def getNowtime(self):
        #return time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        return time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))

    def createdir(self):
        dirname = self.recorddir + os.path.sep + self.getNowtime()
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
        return dirname
    def url2name(self,url):
        tmpurl=url
        if url.startswith('http'):
            tmpurl=url.replace('http://', '')
            tmpurl = tmpurl.replace('https://', '')
        if tmpurl.endswith('/'):
            tmpurl=tmpurl[:-1]
        tmpurl = tmpurl.replace('/', '-')
        return tmpurl


    def start(self,rule_types):
        rules = get_rules(rule_types)
        if len(rules) == 0:
            logger.critical('get rules failed, rule types not found!')
            exit(0)
        self.rulenum = len(rules)
        logger.info('rules length: {rl}'.format(rl=len(rules)))
        #tmptime=self.getNowtime()
        #dirname = self.recorddir + tmptime
        self.dirname = self.createdir()
        #dirname = self.recorddir
        #pool = mp.Pool()
        result_list = []
        webshotargs = []
        for idx, rule_object in enumerate(rules):
            #print(idx, rule_object.url)
            logger.info('>>>>>>>>>>>>> {n} > {r} >>>>>>'.format(n=rule_object.types, r=rule_object.url))
            urlname = self.url2name(rule_object.url)+'-'+self.getNowtime()
            content = self.openWebPage(rule_object.url)
            sourcefile = None


            #html = '<h1>网页监控报告: {rule_regex} Count: {count} Datetime: {datetime}</h1>'.format(
            #    rule_regex=self.rule_object.keyword, datetime=time.strftime("%Y-%m-%d %H:%M:%S"),
            #    count=len(self.content))

            tmp = []
            tmp.append(rule_object.url)
            if content  :

                sourcefile = self.dirname + os.path.sep + urlname + '.txt'

                #sourcemd5= self.md5_ncrypt(content)


                with open(sourcefile, 'w',encoding='utf-8') as f:
                    f.write(content)
                sourcemd5 = self.md5sum(sourcefile)
                #oldmd5 = queryUrlMd5(self.dbfile, self.table_name, rule_object.url)

                picname = self.dirname + os.path.sep + urlname + '.png'
                filename = self.dirname + os.path.sep + urlname
                #webshot(filename, rule_object.url)
                webshotargs.append((picname, rule_object.url))


                tmp = (rule_object.url, sourcemd5, sourcefile, picname)
                result_list.append(tmp)
            else:
                tmp = (rule_object.url,'null','null','null')
                result_list.append(tmp)
        webshotmp(webshotargs)
        self.checkdiff(result_list)


            #pool.apply_async(search, args=(idx, rule_object), callback=store_result)
        #pool.close()
        #pool.join()

    def genratepagelist(self,pagelist):
        html=''
        for record in pagelist:
            html += '<li> URL地址: {url}    MD5: {md5}   源码路径:  {source}  截图路径: {img} </li>'.format(
                url=record[0], md5=record[1], source=record[2], img=record[3])
        return html


    def checkdiff(self, result_list):
        count = len(result_list)
        #normal new  change error
        result_dict={}
        pagenew = []
        pagenormal = []
        pageerror = []
        pagechanged = []
        for record in result_list:
            #print (record[0])
            url, pagemd5, sourfile, imgname = record

            if pagemd5 == 'null':
                #页面打开失败
                pageerror.append(record)
            else:
                oldmd5 = queryUrlMd5(self.dbfile, self.table_name,url)

                if oldmd5 :
                    if oldmd5 == pagemd5 :
                        pagenormal.append(record)
                    else:
                        pagechanged.append(record)
                else:
                    pagenew.append(record)
        write_db('%s' % self.dbfile, self.table_name, result_list)
        #print ('normal page', pagenormal)
        #print ('page error', pageerror)
        #print ('page new', pagenew)
        #print ('page changed', pagechanged)
        reporttime = time.strftime("%Y-%m-%d %H:%M:%S")
        subject = "网站防篡改监控报告--{ss}".format(ss=reporttime)

        html = '<h1>监控网站数量: {count} 监控时间: {datetime}</h1><HR>'.format(count=self.rulenum,
                                                                           datetime=reporttime)
        #html +='<HR style="FILTER: alpha(opacity=100,finishopacity=0,style=3)"  color=#987cb9 SIZE=3>'
        #所有页面正常
        print (self.rulenum,'-----------',len(pagenormal))
        if self.rulenum == len(pagenormal):
            html += '<h3> 所有被监控网页正常运行无异常！ </h3>'
            html += self.genratepagelist(pagenormal)
            Notification(subject).sendmail(html=html)
        else:
            if len(pageerror):
                #html += '<h3 style="color:red ; font-size:50px">'
                html += '</br><h3 style="color:red ; ">访问异常网站{count}个，分别为如下网站</h3>'.format(count=len(pageerror))
                html += self.genratepagelist(pageerror)
            if len(pagechanged):
                html += '</br><h3 style="color:red ; ">页面变化网站{count}个，请人工确认，分别为如下网站</h3>'.format(count=len(pagechanged))
                html += self.genratepagelist(pagechanged)
            if len(pagenew):
                html += '</br><h3 style="color:red ; ">新增监控网站{count}个，分别为如下网站</h3>'.format(count=len(pagenew))
                html += self.genratepagelist(pagenew)
            if len(pagenormal):
                html += '</br><h3 >运行正常网站{count}个，分别为如下网站</h3>'.format(count=len(pagenormal))
                html += self.genratepagelist(pagenormal)
            zipfilename = '网站防篡改监控运行日志-' + reporttime.replace(':','').replace('-','') + '.zip'
            if self.zipDir(self.dirname,zipfilename):
                #print("qqqq")
                Notification(subject).sendmail(html=html,attchfile=zipfilename)
                os.remove(zipfilename)

    def zipDir(self,dirpath, outFullName):
        """
        压缩指定文件夹
        :param dirpath: 目标文件夹路径
        :param outFullName: 压缩文件保存路径+xxxx.zip
        :return: 无
        """
        try:
            #if 'nt' == os.name: 
            #    zip = zipfile.ZipFile(outFullName, "w")
            #else:

            #    zip = zipfile.ZipFile(outFullName, "w", zipfile.ZIP_DEFLATED)
            zip = zipfile.ZipFile(outFullName, "w")
            for path, dirnames, filenames in os.walk(dirpath):
                # 去掉目标跟路径，只对目标文件夹下边的文件及文件夹进行压缩
                #print(fpath)
                fpath = path.replace(dirpath, '')

                #print(fpath)
                for filename in filenames:
                    zip.write(os.path.join(path, filename), os.path.join(fpath, filename))
            zip.close()
            return True
        except:
            logger.error("genrate zip file  error {dir}   {name}".format(dir=dirpath,name=outFullName))
            return False




    def main(self):
#        t = time.time()
        #pool = multiprocessing.Pool(multiprocessing.cpu_count())
#        self.start('single')
#        logger.info("操作结束，耗时：{:.2f}秒".format(float(time.time() - t)))
        while 1:
            t = time.time()
            self.start('single')
            logger.info("操作结束，耗时：{:.2f}秒".format(float(time.time() - t)))
            time.sleep(self.timeinterval)
#            






    #访问URL
    def openWebPage(self,url):
        tag = 0
        while tag < int(self.retriesnum):
            try:
                if tag != 0 :
                    time.sleep(self.fail_time_interval_num + random.randint(1, 5))
                page = requests.get(url, headers=req_headers, allow_redirects=True)
                return page.text
            except:
                print(u"网络访问失败! ")
                logger.error('open {url} fail ,fail num is {tag} '.format(url=url, tag=tag+1))
                tag +=1
                
        return None


def webshotmp(args):
    t = time.time()
    pool = mp.Pool()
    logger.info('webshot {filename}  {url}'.format(filename=args[0],url=args[1]))
    #pool.map_async(func=webshot, iterable=args)
    for aa in args:
        logger.info('webshot {filename}  {url}'.format(filename=aa[0],url=aa[1]))
        pool.apply_async(webshot,args=(aa,))
    #pool.map(webshot, args)
    pool.close()
    pool.join()
    print("操作结束，耗时：{:.2f}秒".format(float(time.time() - t)))

if __name__ == '__main__':
    newVisit = WebpageMonitor()
    newVisit.main()
    #newVisit.save_result()
