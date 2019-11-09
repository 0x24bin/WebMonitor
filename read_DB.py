# -*- coding:utf-8 -*-

import sqlite3


# 创建表
def create_table(db_name, table_name):
    conn = sqlite3.connect('%s' % db_name)
    cursor = conn.cursor()
    cursor.execute("create table %s (id INTEGER PRIMARY KEY AUTOINCREMENT,url text not null,pagemd5 text not null,sourcefile text not null,picname text not null,date timestamp not null default (datetime('now','localtime')))"%table_name,)
    cursor.close()
    conn.close()


# 读取数据库
def queryUrlMd5(db_name, table_name, url, size=100):
    conn = sqlite3.connect('%s' % db_name)
    cursor = conn.cursor()
    cursor.execute("select pagemd5 from %s  where url = '%s' order by date desc limit 0,1" % (table_name,url))
    result_all = cursor.fetchmany(size)
    cursor.close()
    conn.close()
    if result_all:
        return result_all[0][0]
    return None

    #return result_all[0]




# 写入数据库
# 由于写入数据库比较耗时,直接将更新的所有传递给write_db
def write_db(db_name, table_name, result_list):
    conn = sqlite3.connect('%s' % db_name)
    cursor = conn.cursor()
    new_list = []
    for result in result_list:
        url,pagemd5, sourfile, imgname = result
        if pagemd5 != 'null':
            sql = "insert into %s (url, pagemd5, sourcefile, picname ) values ('%s', '%s', '%s', '%s')" % (table_name, url,pagemd5, sourfile, imgname)
            #print(sql)
            #cursor.execute(sql)
            #conn.commit()
            try:
                cursor.execute(sql)
                new_list.append(result)
                conn.commit()
                print(u"写入  "+sql+u" 成功！")
            except:
                print(result+u" 已存在！")
    cursor.close()
    conn.close()
    return True
    #return new_list


if __name__ == '__main__':
    #create_table('test', 'test')
    aa = queryUrlMd5('aaa.db','result','http://www.suningestate.com/index.aspxa')
    if aa:
        print (aa)
    #print(querymd5('aaa.db','result','http://www.suningestate.com/index.asp'))


