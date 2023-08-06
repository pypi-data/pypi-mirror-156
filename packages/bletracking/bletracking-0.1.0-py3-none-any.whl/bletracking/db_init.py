from helpers.SQLite import SQLite


def db_init():
    try:
        with SQLite('tracker.db') as cur:
            cur.execute('''
                CREATE TABLE trackers (
                    id TEXT NOT NULL UNIQUE ,
                    is_in_area TEXT NOT NULL ,
                    mcid TEXT NOT NULL 
                );
            ''')
    except Exception as error:
        pass
