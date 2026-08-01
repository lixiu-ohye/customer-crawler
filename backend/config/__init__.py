# -*- coding: utf-8 -*-
"""生产 MySQL 支持：pymysql 伪装 MySQLdb（Django 4.2 连接 MySQL 必需）"""
import pymysql

pymysql.install_as_MySQLdb()
