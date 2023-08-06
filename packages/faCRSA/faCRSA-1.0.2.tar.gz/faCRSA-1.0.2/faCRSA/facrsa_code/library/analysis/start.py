#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：facrsa_code
@File ：start.py
@Author ：Ruinan Zhang
@Mail: 2020801253@stu.njau.edu.cn
@Describe : Analysis Processing
"""
from facrsa_code.library.analysis.processing import imgProcessing
from facrsa_code.library.analysis import rootanalysis
from facrsa_code.library.analysis.predict import imgPredict
from facrsa_code.library.analysis.postaction import postAction
from facrsa_code.library.analysis.database.writermysql import csv_to_mysql, update_schedule, \
    update_task, \
    update_task_error
from facrsa_code.library.analysis.errorcheck import send_mail_user


def start(conf, uid, tid):
    try:
        res = analysis_single(conf, uid, tid)
        if res == '1':
            return '1'
    except(AttributeError, OverflowError, IndexError, NameError) as e:
        msg = "Task execution failed. Please resubmit the task."
        send_mail_user(msg, conf)
        update_schedule(tid, "999")
        update_task_error(tid)
        print(e)
        exit()


def analysis_single(conf, uid, tid):
    # insert_schedule(tid)
    input_action = imgProcessing(conf)
    # update_schedule(tid, "1")
    img_list = input_action.get_imglist(0)
    file_array = input_action.get_file_array()
    predict = imgPredict(conf)
    predict.initial_predict(list(img_list))
    input_action.initial_merge_img(0)
    input_action.initial_merge_img(1)
    input_action.initial_merge_img(2)
    input_action.initial_merge_img(3)
    # update_schedule(tid, "1*2")
    p_img = input_action.get_imglist(1)
    rootanalysis.rootAnalysis(p_img, conf, file_array, tid)
    csv_to_mysql(conf["out_path"] + "result.csv", tid, uid)
    # update_schedule(tid, "1*2*3")
    move_file = postAction(conf, uid, tid, 1)
    move_file.move_file()
    move_file.restore_image_name(file_array, tid, uid)
    move_file.remove_folder()
    move_file.zipfile()
    move_file.send_mail()
    # move_file.set_status()
    update_task(tid)
    return '1'
    # update_schedule(tid, "1*2*3*4")
