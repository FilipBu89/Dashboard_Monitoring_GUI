import os, sys
import pandas as pd
import json
from pandas import DataFrame
from typing import Tuple, List, Any
import pyodbc
import sqlite3
from Utilities.utils import SQLite


columns_rename = {
    "Company Name": "CompanyName",
    "Connection Name": "ConnectionName",
    "Configuration Name": "ConfigurationName",
    "Filename": "Filename",
    "Identifier": "Identifier",
    "Worker": "Worker",
    "Type": "Type",
    "Description": "Description",
    "Description business": "DescriptionBusiness",
    "Date": "Date",
    "Data Owner": "DataOwner"
}

def load_sql_database(database: str) -> None:
    """Load data from MS SQL database and returns a connec object

    PARAMETERS:
    database: name of the database from which data should be pulled

    Rest of the connection attributes are all hardcoded since its only for personal use
    """
    connection = pyodbc.connect("Driver={{ODBC Driver 17 for SQL Server}};"
                                "SERVER=sqlmi-collection-euw-prod-01.6bb227563724.database.windows.net;"
                                "DATABASE={database};"
                                "UID=filip.bunta@fefundinfo.com;"
                                "Authentication=ActiveDirectoryInteractive".format(**locals()))
    return connection

def load_csv_data(filename: str, database_name, table_name: str) -> None:
    """"Load data from csv file into SQL table using pandas

    PARAMETERS:
    filename: input filename along with extension, which is expectd to be .csv
    database_name: name of the SQLite database to which we are connecting
    table_name: name of the database table, where data should be loaded
    """
    with SQLite(database_name=database_name) as conn:
        try:
            file_path = os.path.join("Files",filename)
            df = pd.read_csv(file_path,delimiter=',',sheet="Windows-1252")
            df.to_sql(table_name, conn, if_exists='append', index = False)
        except OSError as err:
            print(err)
            sys.exit()
        print(f"Data from '{filename}' file was loaded into table '{table_name}'.")

def load_excel_data(filename: str, connection, table_name: str,
                    max_date, columns_rename_dict: dict = columns_rename,
                    ignore_on_import: list = None) -> Tuple[bool,int]:
    """"Load data from .xlsx file into SQL table using pandas

    PARAMETERS:
    filename: input filename along with extension, which is expectd to be .xlsx
    database_name: name of the SQLite database to which we are connecting
    table_name: name of the database table, where data should be loaded
    """
    max_records = 0
    try:
        file_path = os.path.join("Files",filename)
        df = pd.read_excel(file_path,sheet_name=0,engine="openpyxl")
        if columns_rename_dict:
            df.rename(columns=columns_rename_dict,inplace=True)
        df["Date"] = pd.to_datetime(df["Date"])
        print(df.shape[0])
        if ignore_on_import:
            df = df[~df["ConfigurationName"].isin(ignore_on_import)]# not load invalid rows on raw import
        print(df.shape[0])
        if max_date is None:
            df.to_sql(table_name, connection, if_exists='append', index = False)
            max_records = df.shape[0] 
        else:
            df.loc[df["Date"] > pd.to_datetime(max_date)].to_sql(table_name, connection, if_exists='append', index = False)
            max_records = df.loc[df["Date"] > pd.to_datetime(max_date)].shape[0]
    except OSError as err:
        print(err)
        return False,max_records
        #sys.exit()
    return True, max_records
        #print(f"Data from '{filename}' file was loaded into table '{table_name}'.")

def load_sql_table_into_dataframe(database_name, table_name: str) -> DataFrame:
    """"Load data from sql database into pandas DataFrame

    PARAMETERS:
    cdatabase_name: name of the SQLite database to which we are connecting
    table_name: name of the database table, from where data should be loaded
    """
    with SQLite(database_name=database_name) as conn:
        query = f"""SELECT * FROM {table_name}"""
        df = pd.read_sql(query,conn)
        print(f"Data for table {table_name} loaded.")
        return df

def load_sql_table_into_dataframe2(connection, query: str) -> DataFrame:
    """"Load data from sql database into pandas DataFrame

    PARAMETERS:
    cdatabase_name: name of the SQLite database to which we are connecting
    table_name: name of the database table, from where data should be loaded
    """
    df = pd.read_sql(query,connection)
    return df

def load_sql_query_into_dataframe(database_name, query: str) -> DataFrame:
    """"Load sql query result from database into pandas DataFrame

    PARAMETERS:
    database_name: name of the SQLite database to which we are connecting
    querry:
    """
    with SQLite(database_name=database_name) as conn:
        df = pd.read_sql(query,conn)
        print("SQL query results were loaded into DataFrame.")
        return df

def load_json_data(filename: str,key_attribute: str = None) -> Any:
    """Load json input data into python dictionary object and retur dict directly or specific attribute value.
    
    PARAMETERS:
    filename: full path to json file.
    key_attribute: key-word optional argument, if it is desired to return directly value for specific attribute.
    """
    with open(filename,encoding="utf_8") as fh:
        json_dict = json.load(fh)
    if key_attribute:
        return json_dict[key_attribute]
    return json_dict

def load_txt_data(filename: str) -> str:
    """Load text input data and return as string value
    
    PARAMETERS:
    filename: full path to txt file
    """
    with open(filename,encoding="utf_8") as fh:
        text = fh.read()
    return text
