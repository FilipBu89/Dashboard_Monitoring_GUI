import tkinter
import tkinter.messagebox

class CommentBox(tkinter.Toplevel):
    """Top-level window widget representing a dialog box for inserting text comment.

    
    """
    def __init__(self,parent) -> None:
        super().__init__(parent)
        self.parent = parent
        self.comment = ""
        self.transient(self.parent) #disables minimize and maximize window functionality
        self.title(f"Escalation Commentary")

        @property
        def comment(self) -> str:
            return self.comment

        #Main frame wrapping all nested child objects
        frame = tkinter.Frame(self)
        
        #Initialize and place buttons, checkbox, label
        comment_label = tkinter.Label(frame,text="Provide your comments:")
        comment_label.grid(row=0,column=0,sticky=tkinter.NW,pady=3, padx=3)
        self.comment_entry = tkinter.Text(frame,height=200,width=300)
        self.comment_entry.grid(row=1,column=0,sticky=("n","e","w"),pady=3, padx=3)

        save_button = tkinter.Button(frame, text='Save', underline=0, command=self.save)
        save_button.grid(row=2, column=0, sticky=("n","e","w"), padx=3, pady=3)

        #Cover extending window
        frame.grid(row=0, column=0, sticky=tkinter.NSEW)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        frame.rowconfigure(1, weight=999)
        frame.rowconfigure(2, weight=1)

        window = self.winfo_toplevel()
        window.columnconfigure(0, weight=1)
        window.rowconfigure(0, weight=1)

        self.geometry("{0}x{1}+{2}+{3}".format(200, 100,
                                                      0, 50))
        self.bind("<Escape>", self.close)
        self.bind("<Control-S>", self.save)
        self.protocol("WM_DELETE_WINDOW",self.close)
        self.grab_set()
        self.wait_window()

    def save(self,*ignore):
        self.comment = self.comment_entry.get(1.0,"end-1c")
        if not self.is_comment():
            return
        self.close()

    def is_comment(self) -> bool:
        """Check if comment was inserted
        
        If comment was not provided by user raise a message warning, that comment must be provided.
        """
        if self.comment == "":
            tkinter.messagebox.showwarning("Comment Not Provided","Please provide an escalation reason for this item...")
            return False
        return True

    def close(self,*ignore):
        self.parent.focus_set()
        self.destroy()

class HelpBox(tkinter.Toplevel):
    """Top-level window widget representing a dialog box showing help text.

    """
    def __init__(self,parent, help_text: str) -> None:
        super().__init__(parent)
        self.parent = parent
        self.title(f"Usage & Tips")

        #Main frame wrapping all nested child objects
        frame = tkinter.Frame(self)
        scrollbar = tkinter.Scrollbar(frame, orient=tkinter.VERTICAL)
        scrollbar.grid(row=0,column=1,sticky=("ns"))

        self.text = tkinter.Text(frame,height=700,width=800,yscrollcommand=scrollbar.set)
        self.text.insert(1.0,help_text)
        self.text.grid(row=0,column=0,sticky=("nsew"),pady=3, padx=3)

        scrollbar["command"] = self.text.yview

        #Cover extending window
        frame.grid(row=0, column=0, sticky=tkinter.NSEW)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        window = self.winfo_toplevel()
        window.columnconfigure(0, weight=1)
        window.rowconfigure(0, weight=1)

        self.geometry("{0}x{1}+{2}+{3}".format(700, 800,
                                                      0, 50))
        self.bind("<Escape>", self.close)
        self.protocol("WM_DELETE_WINDOW",self.close)
        self.grab_set()
        self.wait_window()

    def close(self,*ignore):
        self.parent.focus_set()
        self.destroy()        
