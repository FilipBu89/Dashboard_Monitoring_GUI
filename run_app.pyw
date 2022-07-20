import tkinter
import sqlite3
import os
from Windows.main_window import MainWindow
from Utilities.load_data import load_json_data

def main(configuration: dict,current_directory: str):
    # create app
    app = tkinter.Tk()
    path = os.path.join(current_directory,"Images/")
    icon = path + "bookmark.ico"
    app.iconbitmap(icon)
    app.title("publiFund Data Feed IN - Dashboard Monitoring (v0.0)")
    window = MainWindow(app,configuration,current_directory)
    app.protocol("WM_DELETE_WINDOW",window.quit)
    app.mainloop()

if __name__ == "__main__":
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    config_file = "//fefifilestore.file.core.windows.net/brno/Personal Backups/FilipRemote/Python/PubliFund_DataFeedIN_Monitoring/Configuration/Config.json"
    configuration = load_json_data(config_file)
    main(configuration,curr_dir)
