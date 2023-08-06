from sqlite3 import (
    Connection, 
    connect as sqlite_connect,
    Cursor
)
from typing import Dict
from pathlib import Path
from urllib.parse import unquote, urlparse

def connect(uri: str) -> Connection:
    '''
    Takes a uri that points to the database and returns a database connection
    '''
    con = sqlite_connect(uri, uri=True)
    cur = con.cursor()
    # Create the table if there is none
    # _create_table(cur, keys)
    cur.execute('''
        CREATE TABLE IF NOT EXISTS mirror (
            uri TEXT PRIMARY KEY,
            mir TEXT DEFAULT "",
            parent TEXT DEFAULT "",
            children TEXT DEFAULT ""   
        ) WITHOUT ROWID;
    ''')
    return con

def commit(con: Connection) -> str:
    '''
    Saves the state of the database and returns a success/failure string
    '''
    try:
        conn.commit()
        return "success"
    except Exception as e:
        return ("failed due to %s", e)
    

def get_uri(uri: str, con: Connection) -> Dict:
    '''
    Takes a uri and a database connection and returns its metadata as a dict
    '''
    return None

def set_uri(uri: str, data: Dict, con: Connection) -> None:
    '''
    Takes a uri and sets its metadata from a dict
    '''
    return None

def get_key(uri: str, key: str, con: Connection) -> str:
    '''
    Takes a uri and gets the value for the given key
    '''

def set_key(uri: str, key: str, val: str, con: Connection) -> str:
    '''
    Takes a uri and sets the value for the given key
    '''

def get_mirror(con: Connection) -> Dict:
    '''
    Takes a mirror connection and returns the mirror as a nested dict
    '''

def set_mirror(con: Connection, map: Dict) -> str:
    '''
    Sets the whole mirror to the given nested map and returns a success/failure string
    '''

def match_mir(con: Connection, uri, keys: Dict = {}) -> str:
    '''
    Takes a uri and and matches its metadata against the mir (if it exists),
    returning a string describing where they match or not.
    if args are passed, only those keys will be matched
    '''

def exists(uri: str) -> str:
    '''
    Takes a uri and returns whether it exists.
    A url exists if the server will respond
    A file exists if it is on the filesystem
    '''

def _unwrap_keys(sql: list) -> dict:
    '''
    Takes a SELECT result from sqlite and converts it to a dict
    '''
    dictionary = {}
    for item in sql:
        primary_key = item[0]
        d = {}

        data = item[1:]
        for i, val in enumerate(data):
            d.update({columns[i]: val}) # We need to get the columns from the PRAGMA call
        dictionary.update({ primary_key:d })
    return dictionary

def _unwrap_columns(sql: list) -> dict:
    '''
    Takes a PRAGMA table_info result from sqlite and turns it into a list
    '''

def _create_table(cur: Cursor, keys: set) -> str:
    '''
    Creates a table with all of the given keys, returns if successful or not
    '''

def _get_table_info(cur: Cursor) -> dict:
    print(cur.execute('''
        PRAGMA table_info('mirror');
    '''
    ).fetchall())
    
# By convention
    # - every uri has a 'mir' key/value pair. Which points to the uri which mirrors it. This is allowed to be empty (should I enforce it to not be empty?)
    # - every uri has a 'parent' key/value pair. By convention this is usually of the same type as itself, a link or a file
    # - every uri has a 'children' key/value pair. By convention this is the same type as itself and the values are store as a comma separated string of uri's
        # e.g. "https://youtube.com, https://internetarchive.com, https://google.com"
        # For files this would be "file:///home/user/Downloads/video.mp4, "file:///home/user/Downloads/audio.mp4, file:///home/user/Downloads/subtitles.vtt"