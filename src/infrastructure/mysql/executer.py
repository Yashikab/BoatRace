from logging import getLogger

from infrastructure import const
from infrastructure.connector import MysqlConnector

logger = getLogger(__name__)


class MysqlExecuter:
    @classmethod
    def run_query(cls, query: str) -> None:
        try:
            logger.debug("connecteng Mysql.")
            with MysqlConnector(const.MYSQL_CONFIG) as conn:
                cursor = conn.cursor()
                logger.debug("run query.")
                cursor.execute(query)
                # cursor.close()
            logger.debug("query run successfully!")
        except Exception as e:
            logger.error(f"{e}")
            raise e
