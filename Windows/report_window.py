import sqlite3
import tkinter
import tkinter.messagebox
from typing import List
from TkTreectrl import MultiListbox
from Windows.text_boxes import CommentBox
import Utilities.commands as commands
import Utilities.app_queries as app_queries

IDENTIFIER_COL, DESCRIPTION_TYPE_COL = (0,3)

class EscalatedWindow(tkinter.Toplevel):
    """Top-level window widget representing a dialog box for handling items validation.

    PARAMETERS:
    parent:
    identifier:
    connection: SQLite connection object
    """
    def __init__(self,parent,connection: sqlite3.Connection, status_id: int) -> None:
        super().__init__(parent)
        self.parent = parent
        self.connection = connection
        self.status_id = status_id
        #self.transient(self.parent) #disables minimize and maximize window functionality
        self.check_box_status = tkinter.IntVar()
        self.title("Escalated Items")

        #Main frame wrapping all nested child objects
        frame = tkinter.Frame(self)

        #Initialize scrollbars, listbox
        scrollbar_vertical = tkinter.Scrollbar(frame, orient=tkinter.VERTICAL)
        scrollbar_horizontal = tkinter.Scrollbar(frame, orient=tkinter.HORIZONTAL)
        self.list_box = MultiListbox(frame,yscrollcommand=scrollbar_vertical.set,xscrollcommand=scrollbar_horizontal.set)
        self.list_box.config(columns=('Identifier','CompanyName','ConfigurationName','Description','Comment','ValidationDate'))
        self.list_box["selectmode"] = "multiple"

        #Place scrollbars, listbox
        scrollbar_vertical["command"] = self.list_box.yview
        scrollbar_vertical.grid(row=0, column=2, sticky=tkinter.NS)
        scrollbar_horizontal["command"] = self.list_box.xview
        scrollbar_horizontal.grid(row=1, column=0,columnspan=1,sticky=tkinter.EW)
        self.list_box.grid(row=0,column=0,sticky=tkinter.NSEW)
        self.list_box.focus_set()
        
        #Initialize and place buttons, checkbox, label
        validate_label = tkinter.Label(frame,text="Validation Options:")
        validate_label.grid(row=0,column=1,sticky=("n","e","w"),pady=3, padx=3)
        fixed_button = tkinter.Button(frame,text="Fixed",command=self.__move_to_fix)
        junked_button = tkinter.Button(frame,text="Junked",command=self.__move_to_junk)
        ignored_button = tkinter.Button(frame,text="Ignored",command=self.__move_to_ignore)
        select_all_items_checkbox = tkinter.Checkbutton(frame,text="Select All", variable=self.check_box_status,
                                            onvalue=1, offvalue=0, command=self.__select_all_listbox_items)
        fixed_button.grid(row=0,column=1,sticky=("n","e","w"),pady=30, padx=3)
        junked_button.grid(row=0,column=1,sticky=("n","e","w"),pady=59, padx=3)
        ignored_button.grid(row=0,column=1,sticky=("n","e","w"),pady=89, padx=3)
        select_all_items_checkbox.grid(row=0,column=1,sticky=("n","e","w"),pady=170, padx=3)

        #Cover extending window
        frame.grid(row=0, column=0, sticky=tkinter.NSEW)
        frame.columnconfigure(0, weight=999)
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(2, weight=1)
        frame.rowconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        window = self.winfo_toplevel()
        window.columnconfigure(0, weight=1)
        window.rowconfigure(0, weight=1)

        self.geometry("{0}x{1}+{2}+{3}".format(1000, 500,
                                                      0, 50))
        self.bind("<Escape>", self.close)
        self.protocol("WM_DELETE_WINDOW",self.close)
        #self.grab_set()
        #self.wait_window()

    def __move_to_fix(self,*ignore):
        rows = self.list_box.curselection()
        for row in rows:
            item = self.list_box.get(row)
            items = (item[0][IDENTIFIER_COL],item[0][DESCRIPTION_TYPE_COL])
            query = app_queries.validate_escalation_items(items,1)
            commands.update_insert_data(self.connection,query=query)
        self.show_list()

    def __move_to_junk(self,*ignore):
        rows = self.list_box.curselection()
        for row in rows:
            item = self.list_box.get(row)
            items = (item[0][IDENTIFIER_COL],item[0][DESCRIPTION_TYPE_COL])
            query = app_queries.validate_escalation_items(items,0)
            commands.update_insert_data(self.connection,query=query)
        self.show_list()

    def __move_to_ignore(self,*ignore):
        rows = self.list_box.curselection()
        for row in rows:
            item = self.list_box.get(row)
            items = (item[0][IDENTIFIER_COL],item[0][DESCRIPTION_TYPE_COL])
            box_form = CommentBox(self)
            comment = box_form.comment
            if not comment:
                continue
            query = app_queries.validate_escalation_items(items,3,comment)
            commands.update_insert_data(self.connection,query=query)
        self.show_list()

    def show_list(self,*ignore):
        query_result = commands.select_data(self.connection,app_queries.get_escalated_items(self.status_id))
        self.list_box.delete(0,tkinter.END)
        if query_result is not None:
            for row in query_result.fetchall():
                self.list_box.insert(tkinter.END,*row)

    def __select_all_listbox_items(self,*ignore):
        if self.check_box_status.get():        
            self.list_box.select_set(0,tkinter.END)
        else:
            self.list_box.select_clear(0,tkinter.END)

    def close(self,*ignore):
        self.parent.focus_set()
        self.destroy()

class IgnoredWindow(tkinter.Toplevel):
    """Top-level window widget representing a dialog box for handling items validation.

    PARAMETERS:
    parent:
    identifier:
    connection: SQLite connection object
    """
    def __init__(self,parent,connection: sqlite3.Connection, status_id: int) -> None:
        super().__init__(parent)
        self.parent = parent
        self.connection = connection
        self.status_id = status_id
        #self.transient(self.parent) #disables minimize and maximize window functionality
        self.check_box_status = tkinter.IntVar()
        self.title("Ignored Items")

        #Main frame wrapping all nested child objects
        frame = tkinter.Frame(self)

        #Initialize scrollbars, listbox
        scrollbar_vertical = tkinter.Scrollbar(frame, orient=tkinter.VERTICAL)
        scrollbar_horizontal = tkinter.Scrollbar(frame, orient=tkinter.HORIZONTAL)
        self.list_box = MultiListbox(frame,yscrollcommand=scrollbar_vertical.set,xscrollcommand=scrollbar_horizontal.set)
        self.list_box.config(columns=('Identifier','CompanyName','ConfigurationName','Description','Comment','ValidationDate'))
        self.list_box["selectmode"] = "multiple"

        #Place scrollbars, listbox
        scrollbar_vertical["command"] = self.list_box.yview
        scrollbar_vertical.grid(row=0, column=2, sticky=tkinter.NS)
        scrollbar_horizontal["command"] = self.list_box.xview
        scrollbar_horizontal.grid(row=1, column=0,columnspan=1,sticky=tkinter.EW)
        self.list_box.grid(row=0,column=0,sticky=tkinter.NSEW)
        self.list_box.focus_set()
        
        #Initialize and place buttons, checkbox, label
        validate_label = tkinter.Label(frame,text="Validation Options:")
        validate_label.grid(row=0,column=1,sticky=("n","e","w"),pady=3, padx=3)
        fixed_button = tkinter.Button(frame,text="Fixed",command=self.__move_to_fix)
        junked_button = tkinter.Button(frame,text="Escalated",command=self.__move_to_escalate)
        ignored_button = tkinter.Button(frame,text="Junked",command=self.__move_to_junk)
        select_all_items_checkbox = tkinter.Checkbutton(frame,text="Select All", variable=self.check_box_status,
                                            onvalue=1, offvalue=0, command=self.__select_all_listbox_items)
        fixed_button.grid(row=0,column=1,sticky=("n","e","w"),pady=30, padx=3)
        junked_button.grid(row=0,column=1,sticky=("n","e","w"),pady=59, padx=3)
        ignored_button.grid(row=0,column=1,sticky=("n","e","w"),pady=89, padx=3)
        select_all_items_checkbox.grid(row=0,column=1,sticky=("n","e","w"),pady=170, padx=3)

        #Cover extending window
        frame.grid(row=0, column=0, sticky=tkinter.NSEW)
        frame.columnconfigure(0, weight=999)
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(2, weight=1)
        frame.rowconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        window = self.winfo_toplevel()
        window.columnconfigure(0, weight=1)
        window.rowconfigure(0, weight=1)

        self.geometry("{0}x{1}+{2}+{3}".format(1000, 500,
                                                      0, 50))
        self.bind("<Escape>", self.close)
        self.protocol("WM_DELETE_WINDOW",self.close)
        #self.grab_set()
        #self.wait_window()

    def __move_to_fix(self,*ignore):
        rows = self.list_box.curselection()
        for row in rows:
            item = self.list_box.get(row)
            items = (item[0][IDENTIFIER_COL],item[0][DESCRIPTION_TYPE_COL])
            query = app_queries.validate_escalation_items(items,1)
            commands.update_insert_data(self.connection,query=query)
        self.show_list()

    def __move_to_junk(self,*ignore):
        rows = self.list_box.curselection()
        for row in rows:
            item = self.list_box.get(row)
            items = (item[0][IDENTIFIER_COL],item[0][DESCRIPTION_TYPE_COL])
            query = app_queries.validate_escalation_items(items,0)
            commands.update_insert_data(self.connection,query=query)
        self.show_list()

    def __move_to_escalate(self,*ignore):
        rows = self.list_box.curselection()
        for row in rows:
            item = self.list_box.get(row)
            items = (item[0][IDENTIFIER_COL],item[0][DESCRIPTION_TYPE_COL])
            box_form = CommentBox(self)
            comment = box_form.comment
            if not comment:
                continue
            query = app_queries.validate_escalation_items(items,2,comment)
            commands.update_insert_data(self.connection,query=query)
        self.show_list()

    def show_list(self,*ignore):
        query_result = commands.select_data(self.connection,app_queries.get_escalated_items(self.status_id))
        self.list_box.delete(0,tkinter.END)
        if query_result is not None:
            for row in query_result.fetchall():
                self.list_box.insert(tkinter.END,*row)

    def __select_all_listbox_items(self,*ignore):
        if self.check_box_status.get():        
            self.list_box.select_set(0,tkinter.END)
        else:
            self.list_box.select_clear(0,tkinter.END)

    def close(self,*ignore):
        self.parent.focus_set()
        self.destroy()