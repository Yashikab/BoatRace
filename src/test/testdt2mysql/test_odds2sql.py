# python 3.7.5
# coding: utf-8
"""
odds2sqlテスト
"""
import pytest

from domain.model.info import (
    Tansho,
    ThreeRenfuku,
    ThreeRentan,
    TwoRenfuku,
    TwoRentan,
)
from infrastructure.dt2sql import Odds2sql
from infrastructure.getdata_lxml import OfficialOdds

from ..common import CommonMethod


@pytest.mark.run(ordre=6)
class TestOdds2sql(CommonMethod):
    __target_date = 20200512
    __jyo_cd = 21
    __race_no = 1

    # load Official Odds for get keys
    __ood = OfficialOdds

    @pytest.fixture(scope="class", autouse=True)
    def insertdata(self):
        __od2sql = Odds2sql()
        __od2sql.insert2table(
            self.__target_date,
            [self.__jyo_cd],
            {self.__jyo_cd: [self.__race_no]},
        )

    key_set = {"race_id"}
    three_rentan_key = key_set.union(set(ThreeRentan.__annotations__.keys()))
    three_renfuku_key = key_set.union(set(ThreeRenfuku.__annotations__.keys()))
    two_rentan_key = key_set.union(set(TwoRentan.__annotations__.keys()))
    two_renfuku_key = key_set.union(set(TwoRenfuku.__annotations__.keys()))
    one_rentan_key = key_set.union(set(Tansho.__annotations__.keys()))

    race_id = int(f"{__target_date}{__jyo_cd:02}{__race_no:02}")
    three_tan_col_list = ["race_id", "`comb_123`", "`comb_456`", "`comb_654`"]
    three_tan_expected = (race_id, 31.9, 157.4, 544.4)
    three_fuku_col_list = ["race_id", "`comb_123`", "`comb_234`", "`comb_456`"]
    three_fuku_expected = (race_id, 7.6, 24.4, 38.3)
    two_tan_col_list = ["race_id", "`comb_12`", "`comb_45`", "`comb_65`"]
    two_tan_expected = (race_id, 10.2, 28.0, 108.3)
    two_fuku_col_list = ["race_id", "`comb_12`", "`comb_23`", "`comb_45`"]
    two_fuku_expected = (race_id, 7.9, 14.7, 11.6)
    one_tan_col_list = ["race_id", "`comb_1`", "`comb_5`"]
    one_tan_expected = (race_id, 2.7, 1.8)

    @pytest.mark.parametrize(
        "tb_nm, col_list, expected",
        [
            ("odds_3tan_tb", three_tan_col_list, three_tan_expected),
            ("odds_3fuku_tb", three_fuku_col_list, three_fuku_expected),
            ("odds_2tan_tb", two_tan_col_list, two_tan_expected),
            ("odds_2fuku_tb", two_fuku_col_list, two_fuku_expected),
            ("odds_1tan_tb", one_tan_col_list, one_tan_expected),
        ],
    )
    def test_insert2table(self, tb_nm, col_list, expected):
        res_tpl = super().get_targetdata(
            tb_nm, "race_id", self.race_id, col_list
        )
        assert res_tpl == expected
