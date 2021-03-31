import pytest

from domain.model.info import HoldRaceInfo

from ._common import CommonMethod
from infrastructure.repository import MysqlRaceInfoRepositoryImpl


@pytest.mark.run(order=2)
class TestRaceInfoRepository:
    __common = CommonMethod()
    __table_name: str = "holdjyo_tb"

    @pytest.fixture(scope="class", autouse=True)
    def preparation(self):
        self.rir = MysqlRaceInfoRepositoryImpl()
        self.rir.create_table_if_not_exists()

    def test_create_table(self):
        get_set = self.__common.get_columns(self.__table_name)
        expected_set = {
            "datejyo_id",
            "holddate",
            "jyo_cd",
            "jyo_name",
            "shinko",
            "ed_race_no",
        }
        assert get_set == expected_set

    def test_save_data(self):
        holdraceinfo_sample = HoldRaceInfo("サンプル場1", 1, "進行状況", 5)
        self.rir.save_info([holdraceinfo_sample])
        # res_tpl = self.__common.get_targetdata(self.__table_name, "datejyo_id")
