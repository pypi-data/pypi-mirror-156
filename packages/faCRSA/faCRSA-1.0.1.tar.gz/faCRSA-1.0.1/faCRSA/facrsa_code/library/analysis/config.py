#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：facrsa_code
@File ：config.ini
@Author ：Ruinan Zhang
@Mail: 2020801253@stu.njau.edu.cn
@Describe : Define analysis global variables
"""
import os
from facrsa_code.library.util.configUtil import get_config


def return_config(factor, mail, private_plugin, uid, tid):
    base_path = get_config('storage')["local_path"] + "/facrsa_code/upload/" + str(uid) + "/" + str(tid) + "/"
    initial_path = base_path + "/initial/"
    predict_out_path = base_path + "predictout/"
    out_path = base_path + "output/"
    # private_plugin = get_config('storage')["local_path"] + "/" + str(uid) + "/" + str(tid) + "/"
    length_ratio = factor
    area_ratio = factor * factor
    mail = mail
    os.mkdir(predict_out_path)
    os.mkdir(out_path)
    data = {
        'base_path': base_path,
        'initial_path': initial_path,
        'predict_out_path': predict_out_path,
        'out_path': out_path,
        'length_ratio': length_ratio,
        'area_ratio': area_ratio,
        'mail': mail,
        'uid': str(uid),
        'tid': str(tid)
    }
    return data
