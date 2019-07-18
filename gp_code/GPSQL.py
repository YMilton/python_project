# coding: utf-8

from xml.etree.ElementTree import parse
import psycopg2
import pandas as pd


'''向数据库Greenplum录入数据'''
class Server(object):
    def __init__(self, host=None, username=None, password=None, database=None):
        self.host = host
        self.username = username
        self.password = password
        self.database = database

    def __str__(self):
        return 'host: %s, username:%s, password:%s, database:%s'                    % (self.host, self.username, self.password, self.database)


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


def get_gp_conn():
    '''
    读取服务器配置文件，修改服务器数据库编码
    :return: 服务器连接
    '''
    server = Server()
    xml_file = server.parse_xml('sql_configure.xml')
    conn = psycopg2.connect(database=xml_file.database, user=xml_file.username, password=xml_file.password,
                            host=xml_file.host, port="5432")
    return conn


# 批量插入数据到数据库
def insert2gp_df(df, table_name):
    conn = get_gp_conn()
    try:
        cols_name_conn = '('+','.join(df.columns)+')' # 标题连接
        rows_conn = df.apply(con_col, axis=1) # 内容行的连接
        batch_rows_insert_str = ','.join([str(x) for x in rows_conn])
        sql = 'INSERT INTO '+table_name+' %s VALUES %s' % (cols_name_conn,batch_rows_insert_str)
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()
        print('%d data insert success!'% len(rows_conn))
    except Exception as e:
        print(e)
    

# 数据连接处理       
def con_col(row):
    str_row = ["'"+str(x)+"'" for x in row]
    return '('+','.join(str_row)+')'


def query_df(sql):
    conn = get_gp_conn()
    cur = conn.cursor()
    cur.execute(sql)
    desc = cur.description
    rows = cur.fetchall()# all rows in table
    df = pd.DataFrame(rows)
    # 数据列修改
    df.columns = [x[0] for x in desc]
    conn.commit()
    cur.close()
    conn.close()
    print('%d data query success!'% (df.shape[0]))

    return df
