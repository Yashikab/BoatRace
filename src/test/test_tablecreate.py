# python 3.7.5
# coding: utf-8
"""
master2sqlモジュール用単体テスト
"""
import pytest

from domain.model.info import (ChokuzenPlayerInfo, ProgramCommonInfo,
                               ProgramPlayerInfo, ResultCommonInfo,
                               ResultPlayerInfo, Tansho, ThreeRenfuku,
                               ThreeRentan, TwoRenfuku, TwoRentan, WeatherInfo)
from domain.tablecreator import (ChokuzenTableCreator, JyoDataTableCreator,
                                 JyoMasterTableCreator, OddsTableCreator,
                                 RaceInfoTableCreator, ResultTableCreator)
from infrastructure.mysql import MysqlExecuter

from .common import CommonMethod


@pytest.mark.run(order=1)
class TestJyoMasterTableCreator(CommonMethod):
    __table_name: str = 'jyo_master'

    @pytest.fixture(scope='class', autouse=True)
    def insertdata(self):
        # jyomaster
        jmtc = JyoMasterTableCreator(MysqlExecuter)
        jmtc.create_table()

    def test_exist_table(self):
        get_set = super().get_columns(self.__table_name)
        expected_set = {'jyo_name', 'jyo_cd'}
        # カラム名確認
        assert get_set == expected_set

    def test_inserteddata(self):
        res_tpl = super().get_targetdata(
            tb_name=self.__table_name,
            id_name='jyo_cd',
            target_id=1,
            col_list=['jyo_name', 'jyo_cd']
        )
        expected_tpl = ('桐生', 1)
        assert res_tpl == expected_tpl


@pytest.mark.run(order=2)
class TestJyoDataTableCreator(CommonMethod):

    @pytest.fixture(scope='class', autouse=True)
    def insertdata(self):
        jdtc = JyoDataTableCreator(MysqlExecuter)
        jdtc.create_table()

    def test_exist_table(self):
        # カラム名の一致でテスト
        get_set = super().get_columns('holdjyo_tb')

        expected_set = {'datejyo_id', 'holddate', 'jyo_cd',
                        'jyo_name', 'shinko', 'ed_race_no'}
        assert get_set == expected_set


@pytest.mark.run(order=3)
class TestRaceInfoTableCreator(CommonMethod):

    @pytest.fixture(scope='class', autouse=True)
    def insertdata(self):
        rdtc = RaceInfoTableCreator(MysqlExecuter)
        rdtc.create_table()

    ri_col_set = {'race_id', 'datejyo_id'}.union(
        set(ProgramCommonInfo.__annotations__.keys())
    )

    pr_col_set = {'waku_id', 'race_id'}.union(
        set(ProgramPlayerInfo.__annotations__.keys())
    )

    @pytest.mark.parametrize("tb_name, col_set", [
        ('raceinfo_tb', ri_col_set),
        ('program_tb', pr_col_set)
    ])
    def test_exist_table_raceinfo(self, tb_name, col_set):
        # カラム名の一致でテスト
        get_set = super().get_columns(tb_name)
        assert get_set == col_set


@pytest.mark.run(order=4)
class TestChokuzenInfo2sql(CommonMethod):

    @pytest.fixture(scope='class', autouse=True)
    def insertdata(self):
        chokutc = ChokuzenTableCreator(MysqlExecuter)
        chokutc.create_table()

    cc_col_set = {'race_id', 'datejyo_id'}.union(
        set(WeatherInfo.__annotations__.keys())
    )
    cp_col_set = {'waku_id', 'race_id'}.union(
        set(ChokuzenPlayerInfo.__annotations__.keys())
    )

    @ pytest.mark.parametrize("tb_name, col_set", [
        ('chokuzen_cond_tb', cc_col_set),
        ('chokuzen_player_tb', cp_col_set)
    ])
    def test_exist_table_raceinfo(self, tb_name, col_set):
        # カラム名の一致でテスト
        get_set = super().get_columns(tb_name)
        assert get_set == col_set


@pytest.mark.run(order=5)
class TestResultInfoTableCreator(CommonMethod):

    @pytest.fixture(scope='class', autouse=True)
    def insertdata(self):
        restc = ResultTableCreator(MysqlExecuter)
        restc.create_table()

    cols = []
    for var_name, var_type in ResultCommonInfo.__annotations__.items():
        if var_type == WeatherInfo:
            for weather_name, weather_type in WeatherInfo.__annotations__.items():
                cols.append(weather_name)
        else:
            cols.append(var_name)

    rr_col_set = {'race_id', 'datejyo_id'}.union(
        set(cols)
    )
    rp_col_set = {'waku_id', 'race_id'}.union(
        set(ResultPlayerInfo.__annotations__.keys())
    )

    @ pytest.mark.parametrize("tb_name, col_set", [
        ('race_result_tb', rr_col_set),
        ('player_result_tb', rp_col_set)
    ])
    def test_exist_table_raceinfo(self, tb_name, col_set):
        # カラム名の一致でテスト
        get_set = super().get_columns(tb_name)
        assert get_set == col_set


@pytest.mark.run(ordre=6)
class TestOdds2sql(CommonMethod):

    @pytest.fixture(scope='class', autouse=True)
    def insertdata(self):
        oddsct = OddsTableCreator(MysqlExecuter)
        oddsct.create_table()

    key_set = {'race_id'}
    three_rentan_key = key_set.union(set(ThreeRentan.__annotations__.keys()))
    three_renfuku_key = key_set.union(set(ThreeRenfuku.__annotations__.keys()))
    two_rentan_key = key_set.union(set(TwoRentan.__annotations__.keys()))
    two_renfuku_key = key_set.union(set(TwoRenfuku.__annotations__.keys()))
    one_rentan_key = key_set.union(set(Tansho.__annotations__.keys()))

    @pytest.mark.parametrize("tb_name, col_set", [
        ('odds_3tan_tb', three_rentan_key),
        ('odds_3fuku_tb', three_renfuku_key),
        ('odds_2tan_tb', two_rentan_key),
        ('odds_2fuku_tb', two_renfuku_key),
        ('odds_1tan_tb', one_rentan_key)
    ])
    def test_exist_odds_table(self, tb_name, col_set):
        # カラム名の一致でテスト
        get_set = super().get_columns(tb_name)
        assert get_set == col_set
