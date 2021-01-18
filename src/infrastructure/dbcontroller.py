# python 3.7.5
# coding: utf-8
'''
google cloud sql proxyを通して, データを格納する
'''
import json
import os
import subprocess
import time
from logging import getLogger
from pathlib import Path
from stat import S_IXGRP, S_IXOTH, S_IXUSR

import mysql.connector

from domain.const import MODULE_LOG_NAME, MYSQL_CONFIG
from domain.dbcontroller import DatabaseController


class Common:

    @classmethod
    def check_connection(cls):
        logger = \
            getLogger(MODULE_LOG_NAME).getChild(cls.__class__.__name__)
        # 接続を確認する(接続されていなかったら10秒待って再度try)
        # 10回やってだめならerror
        for i in range(10):
            try:
                mysql.connector.connect(**MYSQL_CONFIG)
                logger.info('Confirm connected to mysql.')
                break
            except Exception as e:
                logger.debug(e)
                if i == 9:
                    logger.error(
                        'mysql connecting comfirmation: timeouted')
                else:
                    logger.warning('Not connected to mysql yet.')
                    logger.debug('wait 10sec and retry.')
                    time.sleep(10)


class CloudSqlController(DatabaseController):
    """use cloud sql mysql"""

    def __init__(self):
        self.logger = \
            getLogger(MODULE_LOG_NAME).getChild(self.__class__.__name__)
        self.logger.info('Set path to proxy.')
        pwd = Path(__file__).resolve()
        self.__proxy_dir = pwd.parents[2].joinpath("proxy")
        if not self.__proxy_dir.exists():
            self.logger.debug('Path not exists then create.')
            os.mkdir(self.__proxy_dir)
        self.logger.debug(f'proxy path: {self.__proxy_dir}')

        self.logger.debug('Get Variables from environment.')
        sa_name = os.getenv('SA_NAME')
        prj_name = os.getenv('PROJECT_ID')
        key_name = '_'.join([sa_name, prj_name])
        self.__key_name_json = f'{key_name}.json'
        self.__account_name = f"{sa_name}@{prj_name}.iam.gserviceaccount.com"
        region = os.getenv('GSQL_REGION')
        db_name = os.getenv('GSQL_INSTANCE_NAME')
        self.__instance_name = f"{prj_name}:{region}:{db_name}"

    def build(self):
        os.chdir(self.__proxy_dir)
        if not os.path.exists('cloud_sql_proxy'):
            self.logger.debug('Install cloud_sql_proxy')
            proxy_dl_url = \
                "https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64"
            subprocess.run(["wget",
                            proxy_dl_url,
                            "-O",
                            "cloud_sql_proxy"])
        os.chmod('cloud_sql_proxy',
                 S_IXUSR | S_IXGRP | S_IXOTH)

        if not os.path.exists(self.__key_name_json):
            self.logger.debug('get key')

            subprocess.run([
                "gcloud",
                "iam",
                "service-accounts",
                "keys",
                "create",
                f"{self.__key_name_json}",
                "--iam-account",
                self.__account_name
            ])
        self.logger.info('connect to cloud sql proxy')
        subprocess.Popen(
            ["./cloud_sql_proxy",
             f"-instances={self.__instance_name}=tcp:3306",
             f"-credential_file={self.__key_name_json}"]
        )
        # wait
        time.sleep(5)
        Common.check_connection()

    def clean(self):
        os.chdir(self.__proxy_dir)
        self.logger.debug('kill cloud_sql_proxy connection.')
        cmd1 = ["ps"]
        cmd2 = ["grep", "cloud_sql_proxy"]
        cmd3 = ["awk", "{print $1}"]
        cmd4 = ["xargs", "kill", "-9"]
        pipe = subprocess.Popen(
            cmd1,
            stdout=subprocess.PIPE)
        pipe = subprocess.Popen(
            cmd2,
            stdin=pipe.stdout,
            stdout=subprocess.PIPE
        )
        pipe = subprocess.Popen(
            cmd3,
            stdin=pipe.stdout,
            stdout=subprocess.PIPE
        )
        subprocess.run(
            cmd4,
            stdin=pipe.stdout
        )

        self.logger.debug('delete pri key id from gcp')
        with open(self.__key_name_json, 'r') as f:
            pri_key_json = json.load(f)
        pri_key_id = pri_key_json['private_key_id']
        cmd1 = ["echo", "yes"]
        cmd2 = ["gcloud", "iam", "service-accounts",
                "keys", "delete", pri_key_id,
                "--iam-account", self.__account_name]
        pipe = subprocess.Popen(
            cmd1,
            stdout=subprocess.PIPE
        )
        subprocess.run(
            cmd2,
            stdin=pipe.stdout
        )
        self.logger.debug('delete json key file.')
        os.remove(self.__key_name_json)


class LocalSqlController(DatabaseController):
    """use local mysql db"""

    def __init__(self):
        self.logger = \
            getLogger(MODULE_LOG_NAME).getChild(self.__class__.__name__)
        pwd = Path(__file__).resolve()
        self.__sql_dir = pwd.parents[2].joinpath("local_mysql")
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
        time.sleep(2)

        try:
            subprocess.run(["docker-compose", "up", "-d"])
        except Exception as e:
            self.logger.error(e)
        # wait
        time.sleep(5)
        Common.check_connection()

    def clean(self):
        self.logger.info('Clean local mysql.')
        os.chdir(self.__sql_dir)
        try:
            # 先に前のゾンビ達は処理しておく，なければエラー履くのでスキップ
            subprocess.run(["docker-compose", "down"])
            subprocess.run(["docker", "volume", "rm", "boat_mysql"])
        except Exception as e:
            self.logger.error(e)
