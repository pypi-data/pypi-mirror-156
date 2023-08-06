#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：facrsa_code
@File ：queue.py
@Author ：Ruinan Zhang
@Mail: 2020801253@stu.njau.edu.cn
@Describe : Program entry file
"""
from facrsa_code.library.analysis import start
from facrsa_code.library.analysis import config
from facrsa_code.library.analysis import interact
import logging


def web_action(uid, tid, process_type):
    """
    :param uid:
    :param tid:
    :param process_type: 单张图像 / zip压缩包
    :return:
    """
    # logging.error(uid, tid, process_type)
    data_interact = interact.interact(uid, tid, 0, process_type)
    factor, mail, private_plugin = data_interact.initial_analysis()
    conf = config.return_config(factor, mail, private_plugin, uid, tid)
    start.start(conf, uid, tid)


def command_action():
    pass
