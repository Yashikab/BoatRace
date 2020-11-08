# python 3.7.5
# coding: utf-8
"""
一定期間の過去のデータを取得．
最新データ取得用プログラムではない．
スクレイピングを行い, mysqlにデータを格納
"""
import sys
from abc import ABCMeta, abstractmethod
from logging import getLogger
# from datetime import datetime
from pathlib import Path
from typing import Callable

from module import const
from module.connect import MysqlConnector
from module.getdata import (
    GetHoldPlacePast,
    OfficialProgram,
    OfficialChokuzen,
    OfficialResults,
    OfficialOdds
)


class Data2sqlAbstract(metaclass=ABCMeta):
    @abstractmethod
    def create_table_if_not_exists(self):
        '''
        テーブルがなければ作成する
        '''
        pass

    @abstractmethod
    def insert2table(self):
        '''
        データを挿入する
        '''
        pass


class Data2MysqlTemplate(Data2sqlAbstract):

    def __init__(self,
                 filename_list: list = [],
                 table_name_list: list = [],
                 target_cls: ABCMeta = None):
        self.__filename_list = filename_list
        self.__tb_name_list = table_name_list
        self.target_cls = target_cls

    def create_table_if_not_exists(self) -> None:
        self._run_query_from_paths(self.__filename_list)
        return None

    def insert2table(self, date: int, jyo_cd: int, race_no: int) -> None:
        """直前情報をSQLへ

        日付，会場コード，レース番号を受取る \n
        レース情報を挿入し続けて，直前情報を挿入する \n
        create_tableのようにタイプ分けはしない
        （opを一回の読み込みで終わらせたい）

        Parameters
        ----------
            date: int
                日付，yyyymmdd型
            jyo_cd : int
                会場コード
            race_no : int
                レース番号
        """
        self.logger.info(f'called {sys._getframe().f_code.co_name}.')
        self.logger.debug(f'args: {date}, {jyo_cd}, {race_no}')
        tcls = self.target_cls(race_no=race_no, jyo_code=jyo_cd, date=date)

        # 各種id
        race_id = int(f"{date}{jyo_cd:02}{race_no:02}")
        datejyo_id = int(f"{date}{jyo_cd:02}")

        self._info_insert(
            tb_name=self.__tb_name_list[0],
            id_list=[race_id, datejyo_id],
            info_dict=tcls.getcommoninfo2dict()
        )
        self._waku_all_insert(
            tb_name=self.__tb_name_list[1],
            base_id=race_id,
            callback_func=tcls.getplayerinfo2dict
        )

        return None

    def run_query(self, query: str) -> None:
        """
        クエリを実行する

        Parameters
        ----------
            query :str
                クエリ文
        """
        try:
            self.logger.debug('connecteng Mysql.')
            with MysqlConnector(const.MYSQL_CONFIG) as conn:
                cursor = conn.cursor()
                self.logger.debug('run query.')
                cursor.execute(query)
                # cursor.close()
            self.logger.debug('query run successfully!')
        except Exception as e:
            self.logger.error(f'{e}')

        return None

    def _run_query_from_paths(self, filename_list: list) -> None:
        """
        queryフォルダ内のファイル名を指定してクエリを実行する
        ファイル名はリストで受取，複数のテーブルを一気に作る

        Parameters
        ----------
            filename_list : list
                クエリのファイル名のリスト

        Returns
        -------
            status : int
                成功したら0，失敗したら1
        """
        for filename in filename_list:
            # パスの指定
            query_filepath = \
                Path(__file__).parent\
                              .joinpath('query', filename)\
                              .resolve()
            self.logger.debug(f'run query from {query_filepath}')
            with open(query_filepath, 'r') as f:
                query = f.read()
                self.run_query(query)

        return None

    def _info_insert(self,
                     tb_name: str,
                     id_list: list,
                     info_dict: dict,
                     ommit_list: list = []) -> None:
        """
        選手の情報の辞書からsqlへインサートするsqlを作成し，挿入する
        注意：テーブルのカラムの順番とinfo_dict.keys()の順番が一致していること

        Parameters
        ----------
            tb_name: str
                挿入する対象のテーブル名
            id_list : list
                insertするidたち
            info_dict: dict
                getdataから得られたdict
            ommit_list: list = []
                insertしない要素
        """
        self.logger.debug(f'insert to {tb_name} start.')
        # idを格納する
        insert_value_list = list(map(lambda x: f"{x}", id_list))
        # python3.7から辞書型で順序を保持する
        for i_key in info_dict.keys():
            i_value = info_dict[i_key]
            if type(i_value) is str:
                # ''で囲む
                i_value = f"'{i_value}'"
            elif i_value is None:
                i_value = "null"
            else:
                # "hoge" ならそれで統一する
                i_value = f"{i_value}"
            if i_value not in ommit_list:
                insert_value_list.append(i_value)

        insert_value_content = ', '.join(insert_value_list)
        insert_value = "(" + insert_value_content + ")"

        # sql作成
        # 重複時は無視する
        sql = f"INSERT IGNORE INTO {tb_name} VALUES"
        query = ' '.join([sql, insert_value])
        # 作成したクエリの実行
        self.run_query(query)
        self.logger.debug(f'insert to {tb_name} done.')

        return None

    def _waku_all_insert(self,
                         tb_name: str,
                         base_id: int,
                         callback_func: Callable[[], dict],
                         ommit_list: list = []) -> None:
        """1~6枠の情報をインサートするメソッド

        Parameters
        ----------
            tb_naem: str
            base_id: int
                waku_id = {base_id}{waku}になる
            info_dict_func: Callable[['function'], dict]
                waku情報を取得する関数メソッド
            ommit_list: list
                _info_insertを参照
        """
        self.logger.debug(f'start insert to {tb_name}.')
        # 1~6枠でループ，データ取得でエラーの場合はインサートされない
        for waku in range(1, 7):
            waku_id = int(f"{base_id}{waku}")
            self._info_insert(
                tb_name=tb_name,
                id_list=[waku_id, base_id],
                info_dict=callback_func(waku)
            )
        self.logger.debug(f'completed insert to {tb_name}')


class JyoData2sql(Data2MysqlTemplate):

    __tb_name = 'holdjyo_tb'

    def __init__(self):
        self.logger = \
            getLogger(const.MODULE_LOG_NAME).getChild(self.__class__.__name__)
        super().__init__(
            ['create_jyodata_tb.sql']
        )

    # オーバーライド
    def create_query(self, date: int) -> str:
        """
        日付をyyyymmdd型で受けとり，その日のレース情報をMySQLに挿入する

        Parameters
        ----------
            date: int
            日付，yyyymmdd型
        """
        self.logger.info(f'called {sys._getframe().f_code.co_name}.')
        # 他のテーブルデータのinsertに使う辞書
        self.dict_for_other_tb = {}
        ghp = GetHoldPlacePast(target_date=date)
        hp_str_list = ghp.holdplace2strlist()
        hp_cd_list = ghp.holdplace2cdlist()

        rows = []
        for hp_s, hp_c in zip(hp_str_list, hp_cd_list):
            datejyo_id: str = f'{date}{hp_c:02}'
            hi_dict = ghp.holdinfo2dict(hp_s)
            self.dict_for_other_tb[hp_c] = hi_dict['ed_race_no']
            # TODO: 親クラスに型変換のクラスを作る
            insert_value_list = [datejyo_id, str(date), str(hp_c), f"'{hp_s}'"]
            ommit_list = []
            for i_key in hi_dict.keys():
                i_value = hi_dict[i_key]
                if type(i_value) is str:
                    # ''で囲む
                    i_value = f"'{i_value}'"
                elif i_value is None:
                    i_value = "null"
                else:
                    # "hoge" ならそれで統一する
                    i_value = f"{i_value}"
                if i_value not in ommit_list:
                    insert_value_list.append(i_value)
            insert_value_content = ', '.join(insert_value_list)
            rows.append("(" + insert_value_content + ")")
        insert_rows = ', '.join(rows)
        sql = f"INSERT IGNORE INTO {self.__tb_name} VALUES"
        query = ' '.join([sql, insert_rows])
        self.logger.info(f'{sys._getframe().f_code.co_name} completed.')

        return query


class RaceData2sql(Data2MysqlTemplate):

    def __init__(self):
        self.logger = \
            getLogger(const.MODULE_LOG_NAME).getChild(self.__class__.__name__)
        super().__init__(
            filename_list=['create_raceinfo_tb.sql', 'create_program_tb.sql'],
            table_name_list=['raceinfo_tb', 'program_tb'],
            target_cls=OfficialProgram)


class ChokuzenData2sql(Data2MysqlTemplate):
    """大部分がRaceInfoと似ているが，
    リアルタムデータ取得時のため別クラスにする"""

    def __init__(self):
        self.logger = \
            getLogger(const.MODULE_LOG_NAME).getChild(self.__class__.__name__)
        super().__init__(
            filename_list=[
                'create_chokuzen_cond_tb.sql', 'create_chokuzen_p_tb.sql'],
            table_name_list=['chokuzen_cond_tb', 'chokuzen_player_tb'],
            target_cls=OfficialChokuzen)


class ResultData2sql(Data2MysqlTemplate):
    """結果情報テーブル作成"""

    def __init__(self):
        self.logger = \
            getLogger(const.MODULE_LOG_NAME).getChild(self.__class__.__name__)
        super().__init__(
            filename_list=['create_raceresult_tb.sql',
                           'create_playerresult_tb.sql'],
            table_name_list=['race_result_tb', 'p_result_tb'],
            target_cls=OfficialResults)


class Odds2sql(Data2MysqlTemplate):
    def __init__(self):
        self.logger = \
            getLogger(const.MODULE_LOG_NAME).getChild(self.__class__.__name__)
        ood = OfficialOdds
        self.__tb_name_list = ['odds_3tan_tb',
                               "odds_3fuku_tb",
                               'odds_2tan_tb',
                               "odds_2fuku_tb",
                               "odds_1tan_tb"]
        self.__key_value_list = [ood.rentan_keylist(3),
                                 ood.renfuku_keylist(3),
                                 ood.rentan_keylist(2),
                                 ood.renfuku_keylist(2),
                                 ood.rentan_keylist(1)]

    # オーバーライド
    def create_table_if_not_exists(self):
        zip_list = zip(self.__tb_name_list, self.__key_value_list)
        for tb_name, keylist in zip_list:
            insert_cols_list = ["race_id BIGINT PRIMARY KEY"]
            for key_name in keylist:
                col_name = f"`{key_name}` FLOAT"
                insert_cols_list.append(col_name)
            insert_cols_list.append(
                "FOREIGN KEY (race_id) REFERENCES raceinfo_tb (race_id)")
            insert_cols = ", ".join(insert_cols_list)
            query = f"CREATE TABLE {tb_name} ({insert_cols})"
            super().run_query(query)

    def insert2table(self, date, jyo_cd, race_no):
        self.logger.info(f'called {sys._getframe().f_code.co_name}.')
        ood = OfficialOdds(race_no, jyo_cd, date)
        race_id = f"{date}{jyo_cd:02}{race_no:02}"
        content_dict_list = \
            [ood.three_rentan(), ood.three_renfuku(),
             ood.two_rentan(), ood.two_renfuku(), ood.tansho()]
        for tb_name, content in zip(self.__tb_name_list, content_dict_list):
            super()._info_insert(
                tb_name,
                [race_id],
                content
            )
