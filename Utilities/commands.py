import os
import datetime
import sys
import pandas as pd
import pyodbc
import sqlite3
import Utilities.load_data as load_data
from Utilities.utils import SQLite

def print_output(cursor) -> None:
    """ """
    header = [column[0] for column in cursor.description]
    print(header)
    for row in cursor.fetchall():
        print(row)

def create_table(connection_name,query: str,table_name: str) -> sqlite3.Cursor:
    """Create table storing info about FE manager groups

    If table already exists, then it will be dropped in the first step and created afterwards
    """
    with SQLite(connection_name=connection_name) as conn:
        try:
            cursor = conn.cursor()
            cursor.executescript(query.format(table_name=table_name))
        except sqlite3.OperationalError as err:
            print(f"Incorrect syntax: {err}")
            return
        except sqlite3.Error as err:
            print(err)
            return
        print(f"Table '{table_name}' was created.")
        return cursor

def create_connection(connection_name: str) -> None:
    """Create a database connection to a SQLite database"""
    conn = None
    try:
        conn = sqlite3.connect(connection_name)
        print(sqlite3.version)
    except sqlite3.Error as err:
        print(err)
    finally:
        if conn:
            conn.close()
   
def select_data(connection,query: str,is_script=False) -> sqlite3.Cursor:
    """Select data using sql statement"""
    cursor = connection.cursor()
    try:
        if is_script:
            cursor.executescript(query)
        else:
            cursor.execute(query)
        return cursor
    except sqlite3.Error as err:
        print(err)
        
def update_insert_data(connection,query: str,is_script=False) -> None:
    """Insert data using sql statement"""
    try:
        cursor = connection.cursor()
        if is_script:
            cursor.executescript(query)
        else:
            cursor.execute(query)
        connection.commit()
    except sqlite3.OperationalError as err:
        print(f"Incorrect syntax: {err}")
    except sqlite3.Error as err:
        print(err)
    
def get_data(connection,query: str) -> str:
    """Select data using sql statement and return and store the value to object variable"""    
    cursor = connection.cursor()
    #result = cursor.execute(query.format(**kwargs)).fetchone()
    result = cursor.execute(query).fetchone()
    if result is not None:
        return result[0]    
    else:
        print("No results for query:\n{}".format(query))
        return ""

def select_split_data(connection_name,split_query: str,select_query: str,**kwargs) -> None:
    """ """
    with SQLite(connection_name=connection_name) as conn:
        split_input = get_data(conn,select_query,kwargs)
        if not split_input:
            return
        cursor = conn.cursor()
        cursor.execute(split_query.format(result=split_input))
        print_output(cursor)

#TRY USE @DECORATOR FOR PRINTING OUT MESSAGE DEVIDER
def populate_csv_output(connection_name: str,select_query: str, output_filename: str) -> None:
    """Populate sql query results into CSV"""
    df_results = load_data.load_sql_query_into_dataframe(connection_name,select_query)
    rows_output = df_results.shape[0]
    #df_results.reset_index(inplace=True)
    #df_results.rename(columns={"index": "RowID"},inplace=True)
    print("\n{0} Populate CSV Results {0}".format("-"*30))
    if rows_output > 0:
        try:
            df_results.to_csv(output_filename,index=False)
            print(f"SQL query results were successfully populated into {output_filename}.")
        except PermissionError as err:
            print(f"Close the {output_filename} file and re-run the program...")
            sys.exit()
        except OSError as err:
            print(err)
            sys.exit()
    else:
        print(f"Below SQL query returned no results:\n{select_query}")

def get_tables_info(connection_name) -> None:
    """Get info about all the database tables and tables schema"""
    query_select = """
        PRAGMA table_info({table_name})
        """

    query_get = """
        SELECT name from sqlite_master
        """
    
    def select_table_info(connection,query: str,table_name) -> None:
        """Select data using sql statement"""
        cursor = connection.cursor()
        cursor.execute(query.format(table_name=table_name))
        print_output(cursor)

    def get_tables(connection,query: str) -> str:
        """Select data using sql statement and return and store the value to object variable"""    
        cursor = connection.cursor()
        cursor.execute(query_get)
        return cursor.fetchall()  

    with SQLite(connection_name=connection_name) as conn:
        tables = get_tables(conn,query_get)
        for table in tables:
            table_name = table[0]
            print(f"Table: {table_name}")
            select_table_info(conn,query_select,table_name)
            print("{}\n".format("="*30))

if __name__ == "__main__":
    import doctest
    doctest.testmod()
    
