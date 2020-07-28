# python 3.7.5
# coding: utf-8
'''
pythonスクリプトを使ってDBを立てる＆削除する
'''
import argparse
from logging import getLogger, DEBUG, basicConfig
from module.dbcontroller import LocalSqlController
import time

# logger
logger = getLogger("DbCtl")
logger.setLevel(DEBUG)


def main():
    msg = \
        "MySQL DB to start.\n" \
        "default : local \n" \
        "if use gcs: add opt \"--gcs\""
    parser = argparse.ArgumentParser(
        description=msg
    )
    parser.add_argument(
        '--gcs',
        action='store_true',
        help='if you want to use gcs as MySQL db.'
    )
    args = parser.parse_args()

    if args.gcs:
        logger.info('use google cloud sql.')

    else:
        logger.info('use default')
        local_sql_ctl = LocalSqlController()
        local_sql_ctl.build()
        # testのため
        time.sleep(10)
        local_sql_ctl.clean()


if __name__ == '__main__':
    # このスクリプトから呼び出されるモジュール全体のログ設定を行う
    basicConfig(
        format='[%(asctime)s] %(name)s %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    main()
