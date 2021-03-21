# python 3.7.5
# coding: utf-8
"""
getdataモジュール用単体テスト
"""
import pytest

from infrastructure.getdata_lxml import OfficialOdds
from infrastructure.getter import GetParserContent

from ..common import CommonMethod


class TestOfficialOdds(CommonMethod):
    """
    2020 4月8日 浜名湖(06) 9レースの情報でテスト\n
    http://boatrace.jp/owpc/pc/race/odds3t?rno=9&jcd=06&hd=20200408
    """

    __date = 20200408
    __jyo_code = 6
    __race_no = 9

    # 選手直前情報取得のための前処理
    @pytest.fixture(scope="class")
    def odds(self):
        odds = OfficialOdds(self.__date, self.__jyo_code, self.__race_no)
        return odds

    # 3連単
    @pytest.mark.parametrize(
        "fst, snd, trd, expected",
        [(1, 2, 3, 6.5), (3, 4, 5, 1621.0), (4, 5, 6, 2555.0), (6, 5, 4, 810.9)],
    )
    def test_threerentan(self, fst, snd, trd, expected, odds, mocker):
        filepath = super().get_html_filepath(
            f"odds_3tan_{self.__date}{self.__jyo_code}{self.__race_no}.html"
        )
        lx_content = GetParserContent.file_to_content(filepath, "lxml")
        mocker.patch.object(GetParserContent, "url_to_content", return_value=lx_content)
        assert odds.three_rentan()[f"comb_{fst}{snd}{trd}"] == expected

    # 3連単(欠場を試行)
    @pytest.mark.parametrize(
        "fst, snd, trd, expected",
        [
            (1, 2, 3, 30.1),
            (1, 2, 5, -9999.0),
            (3, 1, 4, 30.2),
        ],
    )
    def test_threerentan_ketsujyo(self, fst, snd, trd, expected, odds, mocker):
        filepath = super().get_html_filepath("odds_3tan_20190103222.html")
        lx_content = GetParserContent.file_to_content(filepath, "lxml")
        mocker.patch.object(GetParserContent, "url_to_content", return_value=lx_content)
        assert odds.three_rentan()[f"comb_{fst}{snd}{trd}"] == expected

    # 3連複
    @pytest.mark.parametrize(
        "fst, snd, trd, expected",
        [(1, 2, 3, 2.9), (2, 3, 4, 160.2), (3, 4, 5, 200.3), (4, 5, 6, 228.9)],
    )
    def test_threerenfuku(self, fst, snd, trd, expected, odds, mocker):
        filepath = super().get_html_filepath(
            f"odds_3fuku_{self.__date}{self.__jyo_code}{self.__race_no}.html"
        )
        lx_content = GetParserContent.file_to_content(filepath, "lxml")
        mocker.patch.object(GetParserContent, "url_to_content", return_value=lx_content)
        assert odds.three_renfuku()[f"comb_{fst}{snd}{trd}"] == expected

    # 2連単
    @pytest.mark.parametrize(
        "fst, snd, expected", [(1, 2, 2.7), (2, 3, 101.3), (3, 4, 238.5), (6, 5, 135.1)]
    )
    def test_tworentan(self, fst, snd, expected, odds, mocker):
        filename = (
            f"odds_2tanfuku_" f"{self.__date}{self.__jyo_code}{self.__race_no}.html"
        )
        filepath = super().get_html_filepath(filename)
        lx_content = GetParserContent.file_to_content(filepath, "lxml")
        mocker.patch.object(GetParserContent, "url_to_content", return_value=lx_content)
        assert odds.two_rentan()[f"comb_{fst}{snd}"] == expected

    # 2連複
    @pytest.mark.parametrize(
        "fst, snd, expected",
        [
            (1, 2, 2.0),
            (2, 3, 25.7),
            (3, 4, 47.1),
        ],
    )
    def test_tworenfuku(self, fst, snd, expected, odds, mocker):
        filename = (
            f"odds_2tanfuku_" f"{self.__date}{self.__jyo_code}{self.__race_no}.html"
        )
        filepath = super().get_html_filepath(filename)
        lx_content = GetParserContent.file_to_content(filepath, "lxml")
        mocker.patch.object(GetParserContent, "url_to_content", return_value=lx_content)
        assert odds.two_renfuku()[f"comb_{fst}{snd}"] == expected

    # 単勝
    @pytest.mark.parametrize("fst, expected", [(1, 1.0), (2, 6.1), (3, 12.2), (6, 9.1)])
    def test_tansho(self, fst, expected, odds, mocker):
        filename = f"odds_1tan_" f"{self.__date}{self.__jyo_code}{self.__race_no}.html"
        filepath = super().get_html_filepath(filename)
        lx_content = GetParserContent.file_to_content(filepath, "lxml")
        mocker.patch.object(GetParserContent, "url_to_content", return_value=lx_content)
        assert odds.tansho()[f"comb_{fst}"] == expected
