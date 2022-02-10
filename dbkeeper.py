import sqlite3
from sqlite3 import Error
import os.path as pth
from enum import Enum

database_path = pth.join('Data', 'databaseb.db')
initiate_script_path = pth.join('Data', 'init.sql')


class UserStates(Enum):
    getting_aquainted = 1
    main_menu = 2
    choosing_video_to_label = 3
    labeling_timecode = 4
    labeling_heroes = 5
    labeling_antiheroes = 6
    labeling_comment = 7
    

class DBKeeper(object):

    def __init__(self, db_file = database_path, init_script_file = initiate_script_path, needInitiate=False):
        self.db_file = db_file
        self.init_script_file = init_script_file
        needInitiate |= not pth.exists(db_file)

        if needInitiate:
            try:
                self._initiateDatabase()
            except Error as e:
                raise e
    
    def _createConnection(self):
        """ create a database connection to the SQLite database
            specified by db_file
        :param db_file: database file
        :return: Connection object or None
        """
        conn = None
        try:
            conn = sqlite3.connect(self.db_file)
            return conn
        except Error as e:
            raise e
    
        return conn

    def _getColumnNames(self, tableName):
        conn = self._createConnection()
        names = None
        try:
            c = conn.cursor()
            script = 'SELECT * FROM {};'.format(tableName)
            c.execute(script)
            names = [description[0] for description in c.description]
        except Error as e:
            raise e
        finally:
            if conn:
                conn.close()
        if conn:
            conn.close()
        
        return names

    def _execute(self, script):
        """ create a table from the create_table_sql statement
        :param conn: Connection object
        :param create_table_sql: a CREATE TABLE statement
        :return:
        """
        conn = self._createConnection()
        
        rows = None
        try:
            c = conn.cursor()
            c.execute(script)
            rows = c.fetchall()
            conn.commit()
        except Error as e:
            raise e
        finally:
            if conn:
                conn.close()
        
        return rows

    def _initiateDatabase(self):
        with open(self.init_script_file) as f:
            script = f.read()
            scripts = [x.strip() for x in script.split(';')]

        for script in scripts:
            if len(script) > 0:
                self._execute(script)
                
    def get_players(self):
        return self._execute("SELECT * FROM users")
                
    def get_players_with_nickname(self, nickname_or_mask):
        return self._execute(f"SELECT * FROM users WHERE nickname LIKE '{nickname_or_mask}'")
    
    def get_players_with_user_id(self, user_id_or_mask):
        return self._execute(f"SELECT * FROM users WHERE user_id LIKE '{user_id_or_mask}'")
    
    def has_player_with_nickname(self, nickname):
        return len(self.get_players_with_nickname(nickname)) > 0
    
    def has_player_with_user_id(self, user_id):
        return len(self.get_players_with_user_id(user_id)) > 0
    
    def add_player(self, user_id, username, nickname):
        self._execute(f"INSERT INTO users (user_id, username, nickname, current_state) VALUES ({user_id}, '{username}', '{nickname}', 1)")
        
    def change_player_nickname(self, user_id, username, new_nickname):
        self._execute(f"UPDATE users SET nickname='{new_nickname}', username='{username}' WHERE user_id = {user_id}")
        
    def set_user_state(self, user_id, user_state):
        self._execute(f"UPDATE users SET current_state={user_state.value} WHERE user_id = {user_id}")
        
    def get_user_state(self, user_id):
        return UserStates(self._execute(f"SELECT current_state FROM users WHERE user_id = {user_id}")[0][0])
                
            
if __name__ == '__main__':
    db = DBKeeper()
    