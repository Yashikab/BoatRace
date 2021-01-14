# テーブル作成用ドメイン
from abc import ABCMeta, abstractmethod


class JyoDataTableCreator(meta=ABCMeta):

    @abstractmethod
    def create_table(self):
        """開催場情報"""
        pass


class RaceInfoTableCreator(meta=ABCMeta):

    @abstractmethod
    def create_commoninfo_table(self):
        """レース共通情報"""
        pass

    @abstractmethod
    def create_playerinfo_table(self):
        """番組表情報"""
        pass


class ChokuzenTableCreator(meta=ABCMeta):

    @abstractmethod
    def create_commoninfo_table(self):
        """直前共通情報"""
        pass

    @abstractmethod
    def create_playerinfo_table(self):
        """直前選手情報"""
        pass


class ResultTableCreator(meta=ABCMeta):

    @abstractmethod
    def create_commoninfo_table(self):
        """結果共通情報"""
        pass

    @abstractmethod
    def create_playerinfo_table(self):
        """結果選手情報"""
        pass


class OddsTableCreator(meta=ABCMeta):

    @abstractmethod
    def create_threerentan_table(self):
        """3連単情報"""
        pass

    @abstractmethod
    def create_threefuku_table(self):
        """3連複情報"""
        pass

    @abstractmethod
    def create_tworentan_table(self):
        """2連単情報"""
        pass

    @abstractmethod
    def create_twofuku_table(self):
        """2連複情報"""
        pass

    @abstractmethod
    def create_tansho_table(self):
        """単勝情報"""
        pass
