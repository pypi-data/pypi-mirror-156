from mindsdb.integrations.mysql_handler.mysql_handler import MySQLHandler


class MariaDBHandler(MySQLHandler):
    """
    This handler handles connection and execution of the MariaDB statements. 
    """

    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)