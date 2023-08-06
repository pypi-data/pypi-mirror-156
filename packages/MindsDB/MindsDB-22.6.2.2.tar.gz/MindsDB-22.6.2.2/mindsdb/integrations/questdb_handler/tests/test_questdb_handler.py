import unittest
from mindsdb.integrations.questdb_handler.questdb_handler import QuestDBHandler
from mindsdb.api.mysql.mysql_proxy.mysql_proxy import RESPONSE_TYPE


class QuestDBHandlerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.kwargs = {
            "host": "127.0.0.1",
            "port": "8812",
            "user": "admin",
            "password": "quest",
            "database": "questdb"
        }
        cls.handler = QuestDBHandler('test_questdb_handler', **cls.kwargs)


    def test_0_check_status(self):
        assert self.handler.check_status()
    
    def test_1_describe_table(self):
        described = self.handler.describe_table("house_rentals_data")
        assert described['type'] is not RESPONSE_TYPE.ERROR
    
    def test_2_get_tables(self):
        tables = self.handler.get_tables()
        assert tables['type'] is not RESPONSE_TYPE.ERROR

    def test_3_select_query(self):
        query = "SELECT * FROM house_rentals_data WHERE 'id'='1'"
        result = self.handler.query(query)
        assert len(result) > 0

