# python 3.7.5
# coding: utf-8
'''
google cloud sql proxyを通して, データを格納する
'''
from logging import getLogger
import os
import subprocess
from abc import ABCMeta, abstractmethod

from module.const import MODULE_LOG_NAME, MYSQL_CONFIG

import mysql.connector
import time

class DatabaseController(metaclass=ABCMeta):
    @abstractmethod
    def build(self):
        """build DB"""
        pass

    @abstractmethod
    def clean(self):
        """del DB"""
        pass


class CloudSqlController(DatabaseController):
    """use cloud sql mysql"""

    def build(self):
        # TODO: Google cloud Mysql接続
        pass

    def clean(self):
        # TODO: Google cloud Mysql接続解除
        pass


class LocalSqlController(DatabaseController):
    """use local mysql db"""
    def __init__(self):
        self.logger = \
            getLogger(MODULE_LOG_NAME).getChild(self.__class__.__name__)
        pwd = os.path.abspath(__file__)
        this_filename = os.path.basename(__file__)
        this_dir = pwd.replace(this_filename, '')
        diff_dir_for_sql = 'br_mkdb/src/module'
        self.__sql_dir = \
            this_dir.replace(diff_dir_for_sql, 'mysql_local/boat')
        self.logger.debug(f'sql dir is {self.__sql_dir}')

    def build(self):
        self.logger.info('Build local mysql.')
        os.chdir(self.__sql_dir)
        try:
            # 先に前のゾンビ達は処理しておく，なければエラー履くのでスキップ
            subprocess.run(["docker-compose", "down"])
            subprocess.run(["docker", "volume", "rm", "boat_mysql"])
        except Exception as e:
            self.logger.warning(e)

        try:
            subprocess.run(["docker-compose", "up", "-d"])
        except Exception as e:
            self.logger.error(e)

        # 接続を確認する(接続されていなかったら10秒待って再度try)
        # 10回やってだめならerror
        for i in range(10):
            try:
                mysql.connector.connect(**MYSQL_CONFIG)
                self.logger.info('Confirm connected to mysql.')
                break
            except Exception:
                if i == 9:
                    self.logger.error(
                        'mysql connecting comfirmation: timeouted')
                else:
                    self.logger.warning('Not connected to mysql yet.')
                    self.logger.debug('wait 10sec and retry.')
                    time.sleep(10)

    def clean(self):
        self.logger.info('Clean local mysql.')
        os.chdir(self.__sql_dir)
        try:
            # 先に前のゾンビ達は処理しておく，なければエラー履くのでスキップ
            subprocess.run(["docker-compose", "down"])
            subprocess.run(["docker", "volume", "rm", "boat_mysql"])
        except Exception as e:
            self.logger.error(e)
