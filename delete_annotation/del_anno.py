# -*-  coding: UTF-8  -*-
"""
    @Author YMilton
"""
import os
import argparse


''' 删除单个文件的注释 '''
def del_file_anno(fileName, newFileName, encode='gbk',
             annoLine="//", annoLines={'begin':'/*', 'end':'*/'}):
    with open(fileName, 'r', encoding=encode) as f:
        content = f.readlines()

    with open(newFileName, 'w', encoding='utf-8') as fw:
        flag = False
        for line in content:
            if annoLine in line:
                continue
            if annoLines['begin'] in line:
                if annoLines['end'] in line:  # /* */在同一行
                    continue
                else:
                    flag = True

            if flag and annoLines['end'] not in line:  # 删除/* */中的内容
                continue
            else:
                flag = False

            if annoLines['end'] in line:
                continue

            fw.write(line)


def del_dir_anno(dir, new_dir):
    # 文件不存在则创建
    if not os.path.exists(new_dir):
        os.mkdir(new_dir)

    fileNames = os.listdir(dir)
    for file in fileNames:
        myFile = os.path.join(dir, file)
        myNewFile = os.path.join(new_dir, file)
        del_file_anno(myFile, myNewFile)
        print(myFile, " process success!")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-dir', type=str, default='./dir/', help='delete annotation directory!')
    parser.add_argument('-new_dir', type=str, default='./new_dir/', help='delete annotation new directory!')
    args = parser.parse_args()
    del_dir_anno(args.dir, args.new_dir)