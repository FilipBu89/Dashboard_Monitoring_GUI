"""Module storing varios usefull classes and functions"""
import pandas as pd
import pyodbc
import sqlite3
import traceback as tb
import os
import shutil
from typing import Any

class SQLite:
    """Context manager object for handling SQLite connection"""
    def __init__(self,connection_name):
        self.connection_name = connection_name
        self.connection = sqlite3.connect(connection_name)

    def __enter__(self):
        print("\n{0} {1} Connection Session {0}\nConnecting to db...\n".format("-"*30,self.connection_name))
        return self.connection
        
    def __exit__(self,exc_type,exc_value, traceback) -> None:
        traceback_msg = tb.format_list(tb.extract_tb(traceback))
        if exc_type == sqlite3.OperationalError:
            print("SQL query error:\n{0}\n\nTraceback:\n{1}".format(exc_value,traceback_msg[0]))
        self.connection.commit()
        self.connection.close()
        print("\nClosing db...")
        if exc_type == sqlite3.OperationalError: #Do not propagate the exception, which was already handled
            return True

def move_file(source_directory: str, destination_directory: str, files: tuple) -> Any:
    """Remove file(s) from source directory and copy file from destination directory back to source directory

    PARAMETERS:
    source_directory:
    destination_directory:
    files:
    """
    for file in files:
        try:
            source_file = os.path.join(source_directory,file)
            dest_file = os.path.join(destination_directory,file)
            if os.path.isfile(source_file):
                os.remove(source_file)
                print(f"Removed file: '{source_file}'")
            shutil.copy(dest_file,source_directory)
            print(f"Moved file '{dest_file}' to '{source_directory}'")
        except PermissionError as err:
            print(f"PermissionError: {err}")
            return err
        except OSError as err:
            return err
            print(f"OSError: {err}")
