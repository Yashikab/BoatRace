from abc import ABCMeta, abstractmethod
from datetime import date
from typing import Iterator

from domain.model.info import OddsInfo


class OddsInfoFactory(metaclass=ABCMeta):

    @abstractmethod
    def getinfo(self, target_date: date) -> Iterator[OddsInfo]:
        raise NotImplementedError()

    @abstractmethod
    def _raceinfo(self, target_date: date, race_no: int) -> OddsInfo:
        raise NotImplementedError()
