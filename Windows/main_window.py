import sqlite3
import datetime
import tkinter
from tkinter.ttk import Combobox
import tkinter.messagebox
from Windows.validation_window import ValidationWindow
from Windows.report_window import EscalatedWindow, IgnoredWindow
from Windows.text_boxes import HelpBox
import os
from typing import List
from TkTreectrl import *
import Utilities.db_tables_queries as queries
import Utilities.commands as commands
import Utilities.load_data as load_data
import Utilities.app_queries as app_queries
import Utilities.utils as utils

class MainWindow:
    """Class representing a main window for dashbaord report application.
    
    Main window is showing a dashboard in form of list of items and allows to filter and refresh results.
    Results are aggregated based on Identifier attribute and full list will be shown and handled in dialog window separately.

    In form of menu bar and also using keyboard short-cuts there is enabled functionality to load data into main database
    from excel source and show list of junked and escalated validated items.

    PARAMETERS:
    parent: tkinter.Tk() app object serving as a parent to MainWindow().
    app_directory: a full string path to main underlying SQLite databse for this application.
    configuration:
    """
    def __init__(self,parent: tkinter.Tk, configuration: dict, app_directory: str) -> None:
        self.parent = parent
        self.configuration = configuration
        self.app_directory = app_directory
        self.description_ignore = configuration["IgnoreDescriptionTypes"]
        self.connection_name = os.path.join(app_directory,"Database",configuration["DatabaseFile"])
        self.help_text = load_data.load_txt_data(os.path.join(configuration["SharedLocation"],"Configuration","help_text.txt"))
        self.date_from_var = tkinter.StringVar()
        self.date_to_var = tkinter.StringVar()
        self.identifier_var = tkinter.StringVar()
        self.config_var = tkinter.StringVar()
        self.filename_var = tkinter.StringVar()
        self.data_type_var = tkinter.StringVar()

        #Menu bar storing import and export data functionalities
        menubar = tkinter.Menu(self.parent)
        self.parent["menu"] = menubar

        #Import menu of the menu bar
        dashboard_menu = tkinter.Menu(menubar)
        for label, command, shortcut_text, shortcut in (
                ("Load from excel", self.load_excel_data, "Ctrl+X", "<Control-x>"),):
            if label is None:
                dashboard_menu.add_separator()
            else:
                dashboard_menu.add_command(label=label, underline=0,
                        command=command, accelerator=shortcut_text)
                self.parent.bind(shortcut, command)
        menubar.add_cascade(label="Import", menu=dashboard_menu, underline=0)

        #Reporting menu of the menu bar
        dashboard_menu = tkinter.Menu(menubar)
        for label, command, shortcut_text, shortcut in (
                ("Escalated items", self.show_escalated_list, "Ctrl+E", "<Control-e>"),
                ("Ignored items", self.show_ignored_list, "Ctrl+I", "<Control-i>")
                ):
            if label is None:
                dashboard_menu.add_separator()
            else:
                dashboard_menu.add_command(label=label, underline=0,
                        command=command, accelerator=shortcut_text)
                self.parent.bind(shortcut, command)
        menubar.add_cascade(label="Reports", menu=dashboard_menu, underline=0)

        # Database load/upload menu of the menu bar
        dashboard_menu = tkinter.Menu(menubar)
        for label, command, shortcut_text, shortcut in (
                ("Load database", self.load_db, "Ctrl+L", "<Control-l>"),
                ("Push database", self.push_db, "Ctrl+P", "<Control-p>"),
                ("Back-up database", self.backup_db, "Ctrl+B", "<Control-b>")
                ):
            if label is None:
                dashboard_menu.add_separator()
            else:
                dashboard_menu.add_command(label=label, underline=0,
                        command=command, accelerator=shortcut_text)
                self.parent.bind(shortcut, command)
        menubar.add_cascade(label="Database", menu=dashboard_menu, underline=0)

        #Help menu of the menu bar
        help_menu = tkinter.Menu(menubar)
        help_menu.add_command(label="Usage & Tips",
                        command=self.help, accelerator="Ctrl+H")
        self.parent.bind("<Control-h>", self.help)
        menubar.add_cascade(label="Help", menu=help_menu, underline=0)

        self.parent.bind("<Control-q>",self.quit)
        #Main frame wrapping all nested child objects
        frame = tkinter.Frame(self.parent)
        
        #Initialize scrollbars, listbox
        scrollbar_vertical = tkinter.Scrollbar(frame, orient=tkinter.VERTICAL)
        scrollbar_horizontal = tkinter.Scrollbar(frame, orient=tkinter.HORIZONTAL)
        self.list_box = MultiListbox(frame,
                                    yscrollcommand=scrollbar_vertical.set,
                                    xscrollcommand=scrollbar_horizontal.set)
        self.list_box.config(command= self.__selection,selectcmd=self.__listbox_copy,
                            columns=('Configuration','Filename',
                                    'Identifier','Date','Items'))

        #self.list_box.bind("<Button-1>",self.listbox_copy)
        #self.list_box["selectbackground"] = "#55FF33"
        #self.list_box["selectforeground"] = "#000000"
        self.list_box["expandcolumns"] = tuple(self.list_box._columns)

        #Place scrollbars, list box
        scrollbar_vertical["command"] = self.list_box.yview
        scrollbar_vertical.grid(row=1, column=3,sticky=tkinter.NS)
        scrollbar_horizontal["command"] = self.list_box.xview
        scrollbar_horizontal.grid(row=2, column=2,sticky=tkinter.EW)
        self.list_box.grid(row=1,column=2,sticky=tkinter.NSEW)
        self.list_box.focus_set()

        #Initialize and place buttons, labels, entry fields
        refresh_button = tkinter.Button(frame, text='Refresh', underline = 0, command=self.show_list)
        refresh_button.grid(row=1, column=0, sticky=tkinter.S, pady=3, padx=3)
        filter_label = tkinter.Label(frame,text="Filter Options")
        date_range_label = tkinter.Label(frame,text="Date Range (yyyy-mm-dd):")
        date_from_label = tkinter.Label(frame,text="From:")
        date_from_entry = tkinter.Entry(frame, textvariable=self.date_from_var)
        date_to_label = tkinter.Label(frame,text="To:")
        date_to_entry = tkinter.Entry(frame, textvariable=self.date_to_var)
        identifier_label = tkinter.Label(frame,text="Identifier:")
        identifier_entry = tkinter.Entry(frame, textvariable=self.identifier_var)
        config_label = tkinter.Label(frame,text="Configuration Name:")
        config_entry = tkinter.Entry(frame, textvariable=self.config_var)
        filename_label = tkinter.Label(frame,text="Filename (use * to match any character):")
        filename_entry = tkinter.Entry(frame, textvariable=self.filename_var)
        data_type_label = tkinter.Label(frame,text="Data Type:")
        data_type_entry = Combobox(frame,values=("All","NAVs","Excluding NAVs"),textvariable=self.data_type_var)
        
        filter_label.grid(row=1,column=0,columnspan=2,sticky=("n","e","w"),pady=3, padx=3)
        date_range_label.grid(row=1,column=0,columnspan=2,sticky=tkinter.NW,pady=50, padx=3)
        date_to_label.grid(row=1,column=1,sticky=tkinter.NW,pady=70, padx=3)
        date_to_entry.grid(row=1,column=1,sticky=tkinter.NW,pady=90, padx=3)
        date_from_label.grid(row=1,column=0,sticky=tkinter.NW,pady=70, padx=3)
        date_from_entry.grid(row=1,column=0,sticky=tkinter.NW,pady=90, padx=3)
        identifier_label.grid(row=1,column=0,sticky=tkinter.NW,pady=120, padx=3)
        identifier_entry.grid(row=1,column=0,columnspan=2,sticky=("n","e","w"),pady=140, padx=3)
        config_label.grid(row=1,column=0,sticky=tkinter.NW,pady=170, padx=3)
        config_entry.grid(row=1,column=0,columnspan=2,sticky=("n","e","w"),pady=190, padx=3)
        filename_label.grid(row=1,column=0,columnspan=2,sticky=tkinter.NW,pady=220, padx=3)
        filename_entry.grid(row=1,column=0,columnspan=2,sticky=("n","e","w"),pady=240, padx=3)
        data_type_label.grid(row=1,column=0,columnspan=2,sticky=tkinter.NW,pady=270, padx=3)
        data_type_entry.grid(row=1,column=0,columnspan=2,sticky=("n","e","w"),pady=290, padx=3)

        #Intialize and place status bar
        self.statusbar = tkinter.Label(frame, text="Ready...",
                                       anchor=tkinter.W)
        self.statusbar.grid(row=3, column=0, columnspan=4,
                            sticky=tkinter.EW)

        frame.grid(row=0, column=0, sticky=tkinter.NSEW)

        #Handle resizing main window, set all the weight to multiple-listbox widget
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(2, weight=999)
        frame.columnconfigure(3, weight=1)
        frame.rowconfigure(0, weight=1)
        frame.rowconfigure(1, weight=999)
        frame.rowconfigure(2, weight=1)
        frame.rowconfigure(3, weight=1)

        window = self.parent.winfo_toplevel()
        window.columnconfigure(0, weight=1)
        window.rowconfigure(0, weight=1)

        self.parent.geometry("{0}x{1}+{2}+{3}".format(850, 650,
                                                      0, 50))
        #self.parent.title()
        self.connection = self.__connect_to_db(self.connection_name)

    def clear_status_bar(self) -> None:
        """Method for clearing status bar text"""
        self.statusbar["text"] = ""

    def set_status_bar(self,text,timeout=5000) -> None:
        """Method for setting the status bar text value"""
        self.statusbar["text"] = text
        if timeout:
            self.statusbar.after(timeout,self.clear_status_bar)

    def show_list(self,*ignore) -> None:
        """Populate items into listbox considering the provided filter option values, if any.
        
        PARAMETERS:
        Returned event values are not used and can be simply ignored.
        """
        my_query = app_queries.get_filter_results(
            date_from=self.date_from_var.get(),
            date_to=self.date_to_var.get(),
            configuration=self.config_var.get(),
            identifier=self.identifier_var.get(),
            filename=self.filename_var.get(),
            data_type=self.data_type_var.get(),
            description_ignore=self.description_ignore
        )
        if my_query == "DateError":
            tkinter.messagebox.showwarning(title="Invalid Date Format",message="Provided date values are not in expected format...")
            return
        
        query_result = commands.select_data(connection=self.connection,
                            query=my_query)
        self.list_box.delete(0,tkinter.END)
        
        if query_result is not None:
            for row in query_result.fetchall():
                self.list_box.insert(tkinter.END,*row)
            count_items = self.list_box.item_count() - 1
            self.set_status_bar(f"Retrieved rows: {count_items}",timeout=False)
        else:
            tkinter.messagebox.showinfo(title="No Results Found",message="No results for used filter options...")

    def show_escalated_list(self,*ignore) -> None:
        """This method is representing.....

        ....
        
        PARAMETERS:
        Returned event values are not used and can be simply ignored.
        """
        new_form = EscalatedWindow(self.parent,self.connection,2)
        new_form.show_list()

    def show_ignored_list(self,*ignore) -> None:
        """This method is representing.....

        ....
        
        PARAMETERS:
        returned event values are not used and can be just ignored.
        """
        new_form = IgnoredWindow(self.parent,self.connection,3)
        new_form.show_list()

    def __selection(self,*ignore) -> None:
        """This method is representing an action triggered by listbox double-click event.

        A new dialog window is opened, where all items under Identifier are shown and handled.
        
        PARAMETERS:
        returned event values are not used and can be just ignored.
        """
        index = self.list_box.curselection()
        item = self.list_box.get(index[0])
        identifier = item[0][2]
        configuration = item[0][0]
        form = ValidationWindow(self,self.parent,identifier,configuration,self.connection,self.description_ignore)
        form.show_list()

    def __listbox_copy(self,*ignore) -> None:
        """Method allowing copying the listbox values on single-click event"""
        self.parent.clipboard_clear()
        index = self.list_box.curselection()
        if not index:
            return
        item = self.list_box.get(index[0])
        filename = item[0][1]
        self.parent.clipboard_append(filename)

    def load_excel_data(self,*ignore) -> None:
        filename = "dataFeedIn_monitoring_errors.xlsx"
        ignore_list = self.configuration["IgnoreConfigurationNameOnImport"]
        self.set_status_bar(f"Importing data from '{filename}'...",timeout=False)
        max_date = commands.get_data(self.connection,queries.get_max_data)
        result, records = load_data.load_excel_data(filename,self.connection,"tblErrorsMonitoring",max_date,ignore_on_import=ignore_list)
        if not result:
            tkinter.messagebox.showwarning(title="File Not Loaded",message="An error occured during import input file...")
        #tkinter.messagebox.showinfo(title="File Loaded",message=f"{records} records from input file '{filename}'"
                                                                #"was loaded and data imported into database...")
        self.set_status_bar(f"From '{filename}' was loaded and imported in database: {records} rows",timeout=False)

    def __connect_to_db(self,connection_name: str):
        conn = sqlite3.connect(connection_name)
        self.set_status_bar(text=f"Connected to local SQLite database: {connection_name}",timeout=False)
        return conn

    def load_db(self,*ignore) -> None:
        """" """
        self.__close_db()
        response = utils.move_file(
            os.path.join(self.app_directory,"Database"),
            os.path.join(self.configuration["SharedLocation"],"Database"), 
            (self.configuration["DatabaseFile"],)
            )
        if not response:
            self.set_status_bar(text=f"Shared database copied to local location...",timeout=False)
        else:
            self.set_status_bar(text=f"Database Copy Error: {response}",timeout=False)
        self.connection = self.__connect_to_db(self.connection_name)

    def push_db(self,*ignore) -> None:
        """" """
        self.__close_db()
        response = utils.move_file(
            source_directory= os.path.join(self.configuration["SharedLocation"],"Database"),
            destination_directory=os.path.join(self.app_directory,"Database"),
            files=(self.configuration["DatabaseFile"],)
            )
        if not response:
            self.set_status_bar(text=f"Local database pushed to shared location...",timeout=False)
        else:
            self.set_status_bar(text=f"Database Copy Error: {response}",timeout=False)
        self.connection = self.__connect_to_db(self.connection_name)

    def backup_db(self, *ignore) -> None:
        """ """
        backup_query = """
        ATTACH DATABASE '{connection_name}' AS curr_db;

        INSERT INTO tblValidationStatus
        SELECT * FROM curr_db.tblValidationStatus;

        INSERT INTO tblStatus
        SELECT * FROM curr_db.tblStatus;
        """
        # check if back-up is already created
        curr_timestamp = str(datetime.date.today())
        backup_filename = "Database/MyDataFeedIN_" + curr_timestamp
        temp_filename = "Database/MyDataFeedIN_Temp"
        backup_file_path = os.path.join(self.configuration["SharedLocation"],backup_filename)
        curr_file_path = os.path.join(self.configuration["SharedLocation"],"Database",self.configuration["DatabaseFile"])
        temp_file_path = os.path.join(self.configuration["SharedLocation"],temp_filename)
        
        if os.path.exists(backup_file_path):
            self.set_status_bar(text=f"Back-up file'{backup_filename}' already exists...",timeout=False)
            print(f"Back-up file'{backup_filename}' already exists...")
            return           
        # new DB handling
        commands.create_connection(temp_file_path)
        commands.create_table(temp_file_path,queries.create_monitoring_table,"tblErrorsMonitoring")
        commands.create_table(temp_file_path,queries.create_validation_table,"tblValidationStatus")
        commands.create_table(temp_file_path,queries.create_status_table,"tblStatus")        
        # current DB handling
        temp_conn = self.__connect_to_db(temp_file_path)
        commands.update_insert_data(
            temp_conn,
            backup_query.format(connection_name=curr_file_path),
            True
        )
        temp_conn.close()
        #self.connection.close()
        # os file renaming/deletion handling
        try:          
            os.rename(curr_file_path,backup_file_path)
            os.rename(temp_file_path,curr_file_path)
            self.set_status_bar(text=f"Created back-up database '{backup_filename}'...",timeout=False)
        except EnvironmentError as err:
            print(err)
            self.set_status_bar(text="Creating database back-up interrupted, check in debug mode...",timeout=False)
        # connect to db file again
        self.connection = self.__connect_to_db(self.connection_name)

    def help(self,*ignore) -> None:
        """"""
        help_box = HelpBox(self.parent,self.help_text)

    def __close_db(self) -> None:
        self.set_status_bar(text=f"Closing database connection...",timeout=False)
        self.connection.commit()
        self.connection.close()

    def quit(self, *ignore) -> None:
        """Exiting method for safe cleaning application and SQLite database.

        PARAMETERS:
        returned event values are not used and can be just ignored.
        """
        self.connection.commit()
        self.connection.close()
        self.parent.destroy()
