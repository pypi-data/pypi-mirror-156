#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：facrsa_code
@File ：interact.py
@Author ：Ruinan Zhang
@Mail: 2020801253@stu.njau.edu.cn
@Describe : Data manipulation
"""
import pandas as pd
import datetime
from facrsa_code.library.util.sqliteUtil import sqliteUtil


def csv_to_mysql(file_name, tid, user):
    data = pd.read_csv(file_name)
    data = data.astype(object).where(pd.notnull(data), None)
    for image, re_img, trl, trpa, tsa, trv, mrl, mrpa, msa, mrv, cha, mrd, trlp, trap, mrlp, mrap in zip(
            data['Image_Name'],
            data['Image_Name'],
            data['Total_Root_Length(cm)'],
            data['Total_Root_Projected_Area(cm2)'],
            data['Total_Surface_Area(cm2)'],
            data['Total_Root_Volume(cm3)'],
            data['Main_Root_Length(cm)'],
            data['Main_Root_Projected_Area(cm2)'],
            data['Main_Root_Surface_Area(cm2)'],
            data['Main_Root_Volume(cm3)'],
            data['Convex_Hull_Area(cm2)'],
            data['Max_Root_Depth(cm)'],
            data['Total_Pixels_Number(L)'],
            data['Total_Pixels_Number(A)'],
            data['Main_Pixels_Number(L)'],
            data['Main_Pixels_Number(A)']):
        try:
            insertsql = "insert into result(trl, trpa, tsa, trv, mrl, mrpa, msa, mrv, cha, mrd, trlp, trap, mrlp, mrap, tid, image,rid) values('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" % (
                trl, trpa, tsa, trv, mrl, mrpa, msa, mrv, cha, mrd, trlp, trap, mrlp, mrap, tid, image, tid)
            sqliteUtil().insert(insertsql)
        except Exception as e:
            print(e)


def insert_schedule(tid):
    schedule = 1
    sql = "insert into schedule(tid,schedule) values('%s','%s')" % (tid, schedule)
    res = sqliteUtil().update(sql)


def update_schedule(tid, schedule):
    sql = "update schedule set schedule = '%s' where tid='%s'" % (schedule, tid)
    res = sqliteUtil().update(sql)


def update_task(tid):
    sql = "update task set status = 1 , update_time='%s' where tid='%s'" % (
        datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), tid)
    res = sqliteUtil().update(sql)


def update_task_error(tid):
    sql = "update task set status = 0 , update_time='%s' where tid='%s'" % (
        datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), tid)
    res = sqliteUtil().update(sql)
