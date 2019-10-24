#!/usr/bin/env python
# coding=utf-8
# @Time    : 2019/10/24 15:02
# @Author  : Linguohu

import json
import time
from datetime import datetime, date, timedelta
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkrds.request.v20140815.DescribeSlowLogsRequest import DescribeSlowLogsRequest
import csv

#初始好cvs文件
def write_excel_xls(path):
    with open(path, "w+", newline='') as file:
        csv_file = csv.writer(file)
        head = ["SQL", "数据库名", "总执行次数", "平均执行时间(秒)", "总执行时间(秒)", "最大执行时长(秒)", "锁定总时长(秒)", "最大锁定时长(秒)", "解析SQL总行数", "解析SQL最大行数",
                "返回SQL总行数", "返回SQL最大行数", "数据生成日期"]
        csv_file.writerow(head)
    print("xls初始数据成功！")

#追加cvs内容
def write_excel_xls_append(path, value):
    with open(path, "a+", newline='') as file:  # 处理csv读写时不同换行符  linux:\n    windows:\r\n    mac:\r
        csv_file = csv.writer(file)
        csv_file.writerows(value)
    print("cvs格式表格【追加】写入数据成功！")


# 返回第4个字段以便排序
def takeSecond(elem):
    return elem[3]

#访问阿里云rds接口返回数据和总数据量
def request_rds(rds_id, PageNumber):
    client = AcsClient('<accessKeyId>', '<accessSecret>', 'cn-hangzhou')
    yesterday = (date.today() + timedelta(days=0)).strftime("%Y-%m-%d")
    today = (date.today() + timedelta(days=0)).strftime("%Y-%m-%d")
    request = DescribeSlowLogsRequest()
    request.set_accept_format('json')

    request.set_DBInstanceId(rds_id)
    request.set_StartTime(yesterday + "Z")
    request.set_EndTime(today + "Z")
    request.set_PageSize("100")
    request.set_PageNumber(PageNumber)
    response = client.do_action_with_exception(request)
    # print(re_json['Items']['SQLSlowLog'][0]['SQLText'])
    re_json = json.loads(str(response, encoding='utf-8'))
    totalRecordCount = re_json['TotalRecordCount']
    return re_json, totalRecordCount

#解析返回的数据并获取相应值写入csv
def save_rds_slowlog(rds_id, xls_name):
    book_name_xls = xls_name + '_' + time.strftime("%Y%m%d%H%M%S", time.localtime()) + '_slowlog.csv'

    write_excel_xls(book_name_xls)
    re_json, totalRecordCount = request_rds(rds_id, 1)
    print("数据一共%s 条" % (totalRecordCount))
    total_page = totalRecordCount // 100
    value = []
    for pagenumber in range(1, total_page + 2):
        print("正在解析%s 页" % (pagenumber))
        re_json, totalRecordCount = request_rds(rds_id, pagenumber)
        for i in re_json['Items']['SQLSlowLog']:
            # print("SQL: %s ,执行时间: %sS" % (i['SQLText'],i['MySQLTotalExecutionTimes']/i['MySQLTotalExecutionCounts']))
            value.append([i['SQLText'], i['DBName'], i['MySQLTotalExecutionCounts'],
                          i['MySQLTotalExecutionTimes'] // i['MySQLTotalExecutionCounts'],
                          i['MySQLTotalExecutionTimes'], i['MaxExecutionTime'],
                          i['TotalLockTimes'], i['MaxLockTime'], i['ParseTotalRowCounts'], i['ParseMaxRowCount'],
                          i['ReturnTotalRowCounts'], i['ReturnMaxRowCount'], i['CreateTime']])
    #排序列表
    value.sort(reverse=True, key=takeSecond)
    write_excel_xls_append(book_name_xls, value)

if __name__ == '__main__':
    save_rds_slowlog("DBInstanceId", "E:\\project\\rds\\a")
    save_rds_slowlog("DBInstanceId", "E:\\project\\rds\\b")