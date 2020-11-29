# python 3.7.5
# coding: utf-8
"""
jyodata2sqlテスト
"""
import pytest
import time

from module.dt2sql import JyoData2sql
from module.getdata import CommonMethods4Official
from ..common import CommonMethod

WAIT = 0.5


@pytest.mark.run(order=2)
class TestJyoData2sql(CommonMethod):

    __target_date = 20200512
    __jyo_cd = 20
    __jd2sql = JyoData2sql()

    @pytest.fixture(autouse=True)
    def insertdata(self, mocker):
        """mock用に共通項にする"""
        soup_content = super().htmlfile2bs4(f'ghp_{self.__target_date}.html')
        mocker.patch.object(CommonMethods4Official, "_url2soup",
                            return_value=soup_content)

        self.__jd2sql.create_table_if_not_exists()
        time.sleep(WAIT)
        self.__jd2sql.insert2table(date=self.__target_date)
        time.sleep(WAIT)

    def test_exist_table(self):
        # カラム名の一致でテスト
        get_set = super().get_columns2set('holdjyo_tb')

        expected_set = {'datejyo_id', 'holddate', 'jyo_cd',
                        'jyo_name', 'shinko', 'ed_race_no'}
        assert get_set == expected_set

    def test_insert2table(self):
        # idの情報を一つ取ってきて調べる
        tb_name = "holdjyo_tb"
        id_name = "datejyo_id"
        target_id = f"{self.__target_date}{self.__jyo_cd:02}"
        col_list = ["datejyo_id", "jyo_cd", "shinko", "ed_race_no"]
        res_tpl = super().getdata2tuple(
            tb_name,
            id_name,
            target_id,
            col_list
        )
        expected_tpl = (
            int(target_id),
            self.__jyo_cd,
            '中止順延',
            0
        )
        assert res_tpl == expected_tpl

    def test_map_raceno_dict(self):
        assert self.__jd2sql.map_raceno_dict[21] == range(1, 13)
