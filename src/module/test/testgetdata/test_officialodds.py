# python 3.7.5
# coding: utf-8
"""
getdataモジュール用単体テスト
"""
import pytest
from module.getdata import (
    CommonMethods4Official,
    OfficialOdds
)
from .common import CommonMethodForTest


class TestOfficialOdds(CommonMethodForTest):
    '''
    2020 4月8日 浜名湖(06) 9レースの情報でテスト\n
    http://boatrace.jp/owpc/pc/race/odds3t?rno=9&jcd=06&hd=20200408
    '''
    __date = 20200408
    __jyo_code = 6
    __race_no = 9

    # 選手直前情報取得のための前処理
    @pytest.fixture(scope='class')
    def odds(self):
        odds = OfficialOdds(
            self.__race_no, self.__jyo_code, self.__date)
        return odds

    # 3連単
    @pytest.mark.parametrize("fst, snd, trd, expected", [
        (1, 2, 3, 6.5),
        (3, 4, 5, 1621.0),
        (4, 5, 6, 2555.0),
        (6, 5, 4, 810.9)
    ])
    def test_threerentan(self, fst, snd, trd, expected, odds, mocker):
        soup_content = super().htmlfile2bs4(
            f'odds_3tan_{self.__date}{self.__jyo_code}{self.__race_no}.html')
        mocker.patch.object(
            CommonMethods4Official, "_url2soup", return_value=soup_content)
        assert odds.three_rentan()[f'{fst}-{snd}-{trd}'] == expected

    # 3連複
    @pytest.mark.parametrize("fst, snd, trd, expected", [
        (1, 2, 3, 2.9),
        (2, 3, 4, 160.2),
        (3, 4, 5, 200.3),
        (4, 5, 6, 228.9)
    ])
    def test_threerenfuku(self, fst, snd, trd, expected, odds, mocker):
        soup_content = super().htmlfile2bs4(
            f'odds_3fuku_{self.__date}{self.__jyo_code}{self.__race_no}.html')
        mocker.patch.object(
            CommonMethods4Official, "_url2soup", return_value=soup_content)
        assert odds.three_renfuku()[f'{fst}-{snd}-{trd}'] == expected

    # 2連単
    @pytest.mark.parametrize("fst, snd, expected", [
        (1, 2, 2.7),
        (2, 3, 101.3),
        (3, 4, 238.5),
        (6, 5, 135.1)
    ])
    def test_tworentan(self, fst, snd, expected, odds, mocker):
        filename = f'odds_2tanfuku_'\
                   f'{self.__date}{self.__jyo_code}{self.__race_no}.html'
        soup_content = super().htmlfile2bs4(filename)
        mocker.patch.object(
            CommonMethods4Official, "_url2soup", return_value=soup_content)
        assert odds.two_rentan()[f'{fst}-{snd}'] == expected

    # 2連複
    @pytest.mark.parametrize("fst, snd, expected", [
        (1, 2, 2.0),
        (2, 3, 25.7),
        (3, 4, 47.1),
    ])
    def test_tworenfuku(self, fst, snd, expected, odds, mocker):
        filename = f'odds_2tanfuku_'\
                   f'{self.__date}{self.__jyo_code}{self.__race_no}.html'
        soup_content = super().htmlfile2bs4(filename)
        mocker.patch.object(
            CommonMethods4Official, "_url2soup", return_value=soup_content)
        assert odds.two_renfuku()[f'{fst}-{snd}'] == expected

    # 単勝
    @pytest.mark.parametrize("fst, expected", [
        (1, 1.0),
        (2, 6.1),
        (3, 12.2),
        (6, 9.1)
    ])
    def test_tansho(self, fst, expected, odds, mocker):
        filename = f'odds_1tan_'\
                   f'{self.__date}{self.__jyo_code}{self.__race_no}.html'
        soup_content = super().htmlfile2bs4(filename)
        mocker.patch.object(
            CommonMethods4Official, "_url2soup", return_value=soup_content)
        assert odds.tansho()[f'{fst}'] == expected
