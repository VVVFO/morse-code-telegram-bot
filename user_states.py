import sqlite3
import bot_config


class UserStateManager:
    def __init__(self, database_name, table_name):
        # create connection
        self.database_name = database_name
        self.table_name = table_name
        self.conn = sqlite3.connect(database_name, check_same_thread=False)
        self.cursor = self.conn.cursor()

        # if table does not exist, then create table
        create_table_statement = """
        CREATE TABLE IF NOT EXISTS {} (
            user_id integer PRIMARY KEY,
            wpm integer NOT NULL,
            frequency integer NOT NULL
            );""".format(table_name)

        self.cursor.execute(create_table_statement)
        self.conn.commit()

    def create_if_not_exist(self, user_id):
        """
        check if user_id has a record in the database
        if not, create one with default values
        """
        insert_statement = """
        INSERT INTO {} (user_id, wpm, frequency)
        VALUES ({}, {}, {})
        """.format(self.table_name,
                   user_id,
                   bot_config.DEFAULT_WPM,
                   bot_config.DEFAULT_FREQUENCY)
        try:
            self.cursor.execute(insert_statement)
            self.conn.commit()
        except sqlite3.IntegrityError:
            pass

    def get_frequency(self, user_id):
        self.create_if_not_exist(user_id)
        select_statement = """
        SELECT frequency
        FROM {}
        WHERE user_id = {}
        """.format(self.table_name, user_id)

        return self.cursor.execute(select_statement).fetchone()[0]

    def set_frequency(self, user_id, new_frequency):
        self.create_if_not_exist(user_id)
        update_statement = """
        UPDATE {}
        SET frequency = {}
        WHERE user_id = {}""".format(self.table_name, new_frequency, user_id)

        self.cursor.execute(update_statement)
        self.conn.commit()

    def get_wpm(self, user_id):
        self.create_if_not_exist(user_id)
        select_statement = """
        SELECT wpm
        FROM {}
        WHERE user_id = {}
        """.format(self.table_name, user_id)

        return self.cursor.execute(select_statement).fetchone()[0]

    def set_wpm(self, user_id, new_wpm):
        self.create_if_not_exist(user_id)
        update_statement = """
        UPDATE {}
        SET wpm = {}
        WHERE user_id = {}""".format(self.table_name, new_wpm, user_id)

        self.cursor.execute(update_statement)
        self.conn.commit()
