import sqlite3
import sys, os
from sqlite3 import Error
from .. import config

""" 
:Globale Variablen
"""
database = "deye.db"
sqlite_table = "deyeinverter"

def create_connection(db_file):
    """ create a database connection to the SQLite database specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return conn


def getpowerconsfromdb():
    connection = sqlite3.connect(database)
    cursor = connection.cursor()

    select_query = "SELECT Value FROM {} WHERE Name = ?".format(sqlite_table)
    cursor.execute(select_query, ("webdata_now_p",))
    result = cursor.fetchone()

    if result:
        return result[0]
    else:
        return None

def getpowersumfromdb():
    connection = sqlite3.connect(database)
    cursor = connection.cursor()

    select_query = "SELECT Value FROM {} WHERE Name = ?".format(sqlite_table)
    cursor.execute(select_query, ("webdata_today_e",))
    result = cursor.fetchone()
    
    if result:
        return result[0]
    else:
        return None

def main():
    global database
    #datena = daten.split(';')
    #print (f"Datum: {datena[1]}")

if __name__ == '__main__':
    main()

