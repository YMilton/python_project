#  -*- coding: utf-8 -*-

import os
import pandas as pd

from xml.etree.ElementTree import parse
from sqlalchemy import create_engine
from dataframe2sb import *

'''向数据库mysql录入数据'''
class Server(object):
    def __init__(self, host=None, username=None, password=None, database=None):
        self.host = host
        self.username = username
        self.password = password
        self.database = database

    def __str__(self):
        return 'host: %s, username:%s, password:%s, database:%s' \
                   % (self.host, self.username, self.password, self.database)


    def parse_xml(self,pathfile):
        '''
        返回数据库服务器对象
        :param pathfile:
        :return:
        '''
        root = parse(pathfile)
        childs = root.findall('server')
        c = childs[0]
        single_object = Server(c.find('host').text, c.find('username').text,
                                 c.find('password').text, c.find('database').text)
        return single_object


def get_mysql_conn():
    '''
    读取服务器配置文件，修改服务器数据库编码
    :return: 服务器连接
    '''
    server = Server()
    xml_file = server.parse_xml('sql_configure.xml')
    url = 'mysql+pymysql://'+xml_file.username+':'+xml_file.password+'@'+xml_file.host+':3306/'+xml_file.database+'?charset=utf8'
    conn = create_engine(url)
    sql = 'alter database '+xml_file.database+' character set utf8'
    conn.execute(sql)
    return conn


def csv2mysql_batch(root_path, conn, tran_arg, append):
    '''
    批量转换数据到数据库
    :param root_path: 批量转换的目录
    :param conn: 数据库连接
    :param tran_arg: 数据转换参数
    :param append: 是否是追加到数据表
    :return:
    '''
    conn.text_factory = str
    listfiles = os.listdir(root_path)
    for filename in listfiles:
        if filename[filename.rfind('.'):] == '.csv':
            with open(root_path + '/' + filename, 'r',encoding='utf-8' ) as f:
                df = pd.read_csv(f, error_bad_lines=False)
            if tran_arg: # 需要转换数据
                df = df_transform(df)

            table_name = filename[:filename.index('.')].lower()
            if append: # 追加数据
                df.to_sql(table_name, conn, if_exists='append', index=False)
            else:
                df.to_sql(table_name, conn, if_exists='replace', index=False)
            # 删除csv文件
            os.remove(root_path + '/' + filename)
    if os.path.exists(root_path):
        os.removedirs(root_path)
    print('Data insert success!')


def csv2mysql_single(csvfile, conn, tran_arg, append):
    '''
    单独一个文件转换到数据库
    '''
    conn.text_factory = str
    if csvfile[csvfile.rfind('.'):] == '.csv':
        with open(csvfile, 'r',encoding='utf-8' ) as f:
            df = pd.read_csv(f, error_bad_lines=False)
        if tran_arg: # 需要转换数据
            df = df_transform(df)

        table_name = csvfile[:csvfile.index('.')].lower()
        if append: #追加
            df.to_sql(table_name, conn, if_exists='append', index=False)
        else:
            df.to_sql(table_name, conn, if_exists='replace', index=False)
    print('Data insert success!')


def df_transform(df):
    '''
    对数据做转置处理
    :param df:
    :return:
    '''
    df = df.T
    ind = df.index.values
    if ind[0] == '地区':
        ind[0] = 'month'
    df.insert(0, 'col', ind)

    # 设置列名
    cols = df.iloc[0, :].values
    # float转int型
    cols = [int(x) if str(x).find('.0') >= 0 else x for x in cols]
    df.columns = cols
    # 删除内容中的
    if df.columns.values[0] == 'month':
        df.drop(['month'], inplace=True)
    if df.columns.values[0] == 'year':
        df.drop(['year'], inplace=True)

    return df


def data2mysql_main(filename, trans_arg=False, append=False):
    '''
    数据库录入
    :param filename: 录入数据库的表名
    :param trans_arg: 数据是否转换
    :param append: 是否追加
    :return:
    '''
    conn = get_mysql_conn()
    # 文件
    if filename[filename.rfind('.'):] == '.csv':
        csv2mysql_single(filename, conn, trans_arg, append)
    # 目录
    else:
        csv2mysql_batch(filename, conn, trans_arg, append)



def csv2mysql_dataframe(df, table_name):
    conn = get_mysql_conn()
    conn.text_factory = str
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    print('Data insert success!')
